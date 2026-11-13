#!/usr/bin/python3

import os
import hmac
import hashlib
import glob
import multiprocessing
import logging as log
import sys

from podop import run_server
from socrate import system, conf

log.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "WARNING"))

def start_podop():
    os.setuid(8)
    url = "http://" + os.environ["ADMIN_ADDRESS"] + "/internal/dovecot/§"
    run_server(0, "dovecot", "/tmp/podop.socket", [
		("quota", "url", url ),
		("auth", "url", url),
		("sieve", "url", url),
    ])

# Actual startup script
os.environ["FRONT_ADDRESS"] = system.get_host_address_from_environment("FRONT", "front")
os.environ["ADMIN_ADDRESS"] = system.get_host_address_from_environment("ADMIN", "admin")
os.environ["ANTISPAM_WEBUI_ADDRESS"] = system.get_host_address_from_environment("ANTISPAM_WEBUI", "antispam:11334")

for dovecot_file in glob.glob("/conf/*.conf"):
    conf.jinja(dovecot_file, os.environ, os.path.join("/etc/dovecot", os.path.basename(dovecot_file)))

os.makedirs("/conf/bin", exist_ok=True)
for script_file in glob.glob("/conf/*.script"):
    out_file = os.path.join("/conf/bin/", os.path.basename(script_file).replace('.script',''))
    conf.jinja(script_file, os.environ, out_file)
    os.chmod(out_file, 0o555)

# Key for the per-user allowlist hook (allowlist.script -> admin). Derived
# from SECRET_KEY the same way mailu/internal/views/dovecot.py does, so the
# raw SECRET_KEY is not written to disk; readable by the mail user only.
with open("/conf/allowlist.key", "w") as handle:
    handle.write(hmac.new(os.environ["SECRET_KEY"].encode(), b"mailu-allowlist", hashlib.sha256).hexdigest())
os.chmod("/conf/allowlist.key", 0o400)

# Run Podop, then postfix
multiprocessing.Process(target=start_podop).start()
os.system("chown mail:mail /mail")
os.system("chown -R mail:mail /var/lib/dovecot /conf")
os.execv("/usr/sbin/dovecot", ["dovecot", "-c", "/etc/dovecot/dovecot.conf", "-F"])
