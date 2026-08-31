import ast
import os
import sys
import types
import pytest

# pkg_resources shim for Python 3.14 where setuptools no longer ships it by default
# passlib imports pkg_resources at top level.
try:
    import pkg_resources  # noqa: F401
except ModuleNotFoundError:
    _pkg = types.ModuleType("pkg_resources")

    def _get_distribution(name):
        class _Dist:
            version = "0.0.0"

        return _Dist()

    _pkg.get_distribution = _get_distribution  # type: ignore
    _pkg.resource_filename = lambda *a, **k: ""  # type: ignore
    _pkg.resource_string = lambda *a, **k: b""  # type: ignore
    sys.modules["pkg_resources"] = _pkg

# Python 3.14 removed ast.Str (and friends) — Werkzeug 2.0 uses it.
# Provide a shim so old Werkzeug can compile its routing on Python 3.14.
try:
    if not hasattr(ast, "Str"):

        def _Str(s=""):
            return ast.Constant(value=s)

        ast.Str = _Str  # type: ignore
    if not hasattr(ast, "Num"):

        def _Num(n=0):
            return ast.Constant(value=n)

        ast.Num = _Num  # type: ignore
except Exception:
    pass

# Werkzeug 2.3 removed safe_str_cmp, Flask-Login 0.5 still imports it.
try:
    import hmac
    import werkzeug.security

    if not hasattr(werkzeug.security, "safe_str_cmp"):
        werkzeug.security.safe_str_cmp = hmac.compare_digest  # type: ignore
except Exception:
    pass

# Python 3.12+ removed distutils — marshmallow 3.14 still imports it.
# Provide a shim via setuptools._distutils before anything imports marshmallow.
try:
    import sys
    import setuptools._distutils  # noqa: F401
    import setuptools._distutils.version  # noqa: F401

    # Expose as `distutils` and `distutils.version` for legacy imports.
    if "distutils" not in sys.modules:
        import setuptools._distutils as _du
        sys.modules["distutils"] = _du
    if "distutils.version" not in sys.modules:
        sys.modules["distutils.version"] = sys.modules["setuptools._distutils.version"]
except Exception:
    pass

# Compatibility shim for Flask-Babel 4.x where Babel.localeselector was removed.
# Mailu's utils.py uses the old decorator API; make it a no-op so import succeeds
# under newer Flask-Babel on Python 3.14 host.
try:
    import flask_babel

    if not hasattr(flask_babel.Babel, "localeselector"):

        def _localeselector(self, func):
            # Flask-Babel 4 uses `locale_selector_func` argument at init time,
            # but the old decorator just returned the function. Mimic that.
            self._test_locale_selector = func
            return func

        flask_babel.Babel.localeselector = _localeselector
except Exception:
    pass

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("DOMAIN", "example.com")
os.environ.setdefault("HOSTNAMES", "mail.example.com")
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite://")
os.environ.setdefault("RECIPIENT_DELIMITER", "+")


@pytest.fixture
def app():
    # Avoid DNS lookups for HOST_* resolution (no cluster DNS on this host)
    try:
        import socrate.system

        socrate.system.resolve_address = lambda x: "127.0.0.1"
    except Exception:
        pass

    from mailu import create_app_from_config, models
    from mailu.configuration import ConfigManager

    config = ConfigManager()
    config.init_app_noop = True
    application = create_app_from_config(config)
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    application.config["TESTING"] = True
    with application.app_context():
        # Mailu's Base uses a separate metadata object; db.create_all() alone
        # creates no tables (verified on this host: 0 tables after db.create_all).
        # Create via Base.metadata instead.
        models.Base.metadata.create_all(bind=models.db.engine)
        yield application
        models.db.session.remove()
        models.Base.metadata.drop_all(bind=models.db.engine)


@pytest.fixture
def make_user(app):
    from mailu import models

    def _make(localpart, domain_name, **kwargs):
        domain = models.Domain.query.get(domain_name)
        if domain is None:
            domain = models.Domain(name=domain_name)
            models.db.session.add(domain)
        user = models.User(localpart=localpart, domain=domain, **kwargs)
        user.set_password("x")
        models.db.session.add(user)
        models.db.session.commit()
        return user

    return _make
