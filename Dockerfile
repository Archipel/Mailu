FROM docker.io/weynwebworks/mailu-admin:b6744e37c7943e7371b97b751e87c93bde5519f8

# CSRF fix overlay — see README.md. Stale .pyc removal so the patched
# configuration.py is guaranteed to be the one that runs.
RUN find /app -name __pycache__ -type d -prune -exec rm -rf {} +
COPY app/mailu/configuration.py /app/mailu/configuration.py
COPY app/mailu/ui/templates/user/create.html /app/mailu/ui/templates/user/create.html

# Sieve-mediated forwarding overlay — see README.md. Relies on the __pycache__
# purge above: a stale models.pyc would shadow the patched models.py.
COPY app/mailu/models.py /app/mailu/models.py
COPY app/mailu/internal/templates/default.sieve /app/mailu/internal/templates/default.sieve
