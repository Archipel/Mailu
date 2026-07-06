FROM docker.io/weynwebworks/mailu-admin:b6744e37c7943e7371b97b751e87c93bde5519f8

# CSRF fix overlay — see README.md. Stale .pyc removal so the patched
# configuration.py is guaranteed to be the one that runs.
RUN find /app -name __pycache__ -type d -prune -exec rm -rf {} +
COPY app/mailu/configuration.py /app/mailu/configuration.py
COPY app/mailu/ui/templates/user/create.html /app/mailu/ui/templates/user/create.html
