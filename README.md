# Recovered source of the deployed mailu-admin image

`app/` is the `/app` tree extracted on **2026-07-06** from the running pod
`mailu-admin-7b6cbf9869-tgkss` (namespace `mailu-mailserver`, cluster `gke-shared`),
i.e. the exact code of the deployed image:

    weynwebworks/mailu-admin:b6744e37c7943e7371b97b751e87c93bde5519f8

The original build source (git commit `b6744e37…`) is not present in the
Archipel/Mailu clone — it was most likely only on a machine that is no longer
available. This branch is the authoritative reference for what runs in
production; `__pycache__` directories were excluded, everything else is
verbatim.

## CSRF patch (Dockerfile in this directory)

Incident 2026-07-06 (mthotelstore.be quota edit "does nothing"): the admin UI
signs form CSRF tokens with a 1-hour lifetime (flask-wtf default) while the
login session lives 24 h. Submitting a form from a page older than 1 h
returns HTTP 200, re-renders the form with the submitted values, saves
nothing and shows **no error** (`hidden_tag()` errors are never rendered).

The overlay image built by `Dockerfile` fixes this on top of the deployed
image, without rebuilding from (lost) source:

1. `mailu/configuration.py` — `WTF_CSRF_TIME_LIMIT: None`: the CSRF token no
   longer has its own expiry; it stays valid for the lifetime of the session
   (24 h), after which the login redirect makes the failure visible anyway.
2. `mailu/ui/templates/user/create.html` (also used by user edit) — renders
   `form.csrf_token.errors` as a visible alert, so any residual CSRF failure
   is no longer silent.

Build & deploy:

    podman build -t weynwebworks/mailu-admin:b6744e37-csrf1 .
    podman push weynwebworks/mailu-admin:b6744e37-csrf1
    kubectl -n mailu-mailserver set image deploy/mailu-admin \
        admin=weynwebworks/mailu-admin:b6744e37-csrf1

Verify after rollout (from inside the admin pod): POST the user-edit form
with a garbage `csrf_token` — the re-rendered page must contain an
`alert-danger` block; a POST with a fresh token must still 302 to the user
list.
