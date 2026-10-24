#!/usr/bin/python3

import hmac
import logging
import os
import subprocess
import sys

import jinja2

env = os.environ
logging.basicConfig(stream=sys.stderr, level=env.get("LOG_LEVEL", "WARNING"))

RC = "/var/www/html"
PHP_CONF = f"/etc/php/{env.get('PHP_VERSION', '8.3')}"


def truthy(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def php_string(value):
    """Render a value as a single-quoted PHP string literal."""
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def render(src, dst, context):
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader("/"), keep_trailing_newline=True)
    jenv.filters["php"] = php_string
    with open(dst, "w") as fh:
        fh.write(jenv.get_template(src).render(context))


# jinja context
context = dict(env)
context["TZ"] = env.get("TZ", "Etc/UTC")
context["MAX_FILESIZE"] = str(int(int(env.get("MESSAGE_SIZE_LIMIT", "50000000")) * 0.66 / 1048576))

db_flavor = env.get("ROUNDCUBE_DB_FLAVOR", "sqlite")
if db_flavor == "sqlite":
    context["DB_DSNW"] = "sqlite:////data/roundcube.db"
elif db_flavor in ("mysql", "postgresql"):
    context["DB_DSNW"] = "%s://%s:%s@%s/%s" % (
        "mysql" if db_flavor == "mysql" else "pgsql",
        env.get("ROUNDCUBE_DB_USER", "roundcube"),
        env.get("ROUNDCUBE_DB_PW"),
        env.get("ROUNDCUBE_DB_HOST", "database"),
        env.get("ROUNDCUBE_DB_NAME", "roundcube"),
    )
else:
    print(f"Unknown ROUNDCUBE_DB_FLAVOR: {db_flavor}", file=sys.stderr)
    exit(1)

secret_key = env.get("SECRET_KEY")
if not secret_key:
    try:
        secret_key = open(env.get("SECRET_KEY_FILE"), "r").read().strip()
    except Exception as exc:
        print(f"Can't read SECRET_KEY from file: {exc}", file=sys.stderr)
        exit(2)

# des_key encrypts the IMAP password kept in the session (and carddav des_key
# passwords). "raw" keeps the key the Mailu 1.8 image used, so open sessions
# survive the upgrade; "derived" is the Mailu 1.9+ HMAC-derived key.
if env.get("ROUNDCUBE_DES_KEY_MODE", "raw") == "derived":
    context["DES_KEY"] = hmac.new(secret_key.encode(), b"ROUNDCUBE_KEY", "sha256").hexdigest()
else:
    context["DES_KEY"] = secret_key

# Mailu SSO needs a front that authenticates and sets X-Remote-User(-Token);
# our webmail ingress goes straight to this container, so it is off by default.
context["SSO"] = truthy(env.get("ROUNDCUBE_SSO", "false"))

# roundcube plugins (dict keeps the order, set does not)
default_plugins = ["archive", "zipdownload", "markasjunk", "managesieve", "enigma", "carddav"]
wanted = [p for p in env.get("ROUNDCUBE_PLUGINS", "").replace(" ", "").split(",") if p] or default_plugins
plugins = dict((p, None) for p in wanted if os.path.isdir(os.path.join(RC, "plugins", p)))
if context["SSO"]:
    plugins["mailu"] = None
context["PLUGINS"] = ",".join(f"'{p}'" for p in plugins)

context["INCLUDES"] = sorted(inc for inc in os.listdir("/overrides") if inc.endswith(".inc")) if os.path.isdir("/overrides") else []

if env.get("SESSION_TIMEOUT"):
    context["SESSION_TIMEOUT_MINUTES"] = max(int(env["SESSION_TIMEOUT"]) // 60, 1)

# create config files
render("php.ini", f"{PHP_CONF}/roundcube.ini", context)
render("config.inc.php", f"{RC}/config/config.inc.php", context)
render("config.inc.carddav.php", f"{RC}/plugins/carddav/config.inc.php", context)
os.chmod(f"{RC}/config/config.inc.php", 0o640)
os.system(f"chgrp www-data {RC}/config/config.inc.php")

os.makedirs("/data/gpg", exist_ok=True)


def run(step, cmd, code, ok_marker=None):
    print(step, flush=True)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode()
    if proc.returncode:
        if ok_marker and ok_marker in out:
            print(f"  skipped ({ok_marker})", flush=True)
            return
        print(out, file=sys.stderr)
        exit(code)
    print(out, flush=True)


run("Initializing database", [f"{RC}/bin/initdb.sh", "--dir", f"{RC}/SQL"], 3, ok_marker="already exists")
# migrates the schema from whatever version the DB is on (1.4 -> 1.6 included)
run("Upgrading database", [f"{RC}/bin/updatedb.sh", "--package=roundcube", f"--dir={RC}/SQL"], 4)
run("Cleaning database", [f"{RC}/bin/cleandb.sh"], 5)

os.system("chown -R www-data:www-data /data")

# clean env
for key in list(env.keys()):
    if key in ("SECRET_KEY", "DB_PW") or key.startswith(("ROUNDCUBE_", "RELAY", "FALLBACK_RELAY", "SIEVE_SMTP_AUTH", "DB_")) or key.endswith(("_MYSQL", "_PASSWORD")):
        env.pop(key, None)

# run apache in the foreground as PID 1
apache_env = dict(env)
for line in subprocess.check_output(["sh", "-c", ". /etc/apache2/envvars && env"]).decode().splitlines():
    if line.startswith("APACHE_"):
        k, _, v = line.partition("=")
        apache_env[k] = v
os.makedirs(apache_env.get("APACHE_RUN_DIR", "/var/run/apache2"), exist_ok=True)
os.makedirs(apache_env.get("APACHE_LOCK_DIR", "/var/lock/apache2"), exist_ok=True)
pid_file = apache_env.get("APACHE_PID_FILE", "/var/run/apache2/apache2.pid")
if os.path.exists(pid_file):
    os.remove(pid_file)
os.execve("/usr/sbin/apache2", ["apache2", "-DFOREGROUND"], apache_env)
