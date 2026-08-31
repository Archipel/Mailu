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

## Sieve-mediated forwarding patch (2026-08-31)

Forwarding moved out of Postfix alias expansion and into the per-user sieve, so a
spam verdict can gate the forward. An alias has no Junk folder, so previously spam
addressed to a forwarder was relayed off-platform under our own IP — the traffic
that got the Mailgun account disabled on 2026-08-25.

Two files:

- `app/mailu/models.py` — `User.resolve_destination` returns only the local mailbox
  for a forwarding user, so Postfix delivers locally instead of expanding to the
  off-platform address.
- `app/mailu/internal/templates/default.sieve` — a `redirect` per destination, plus
  `keep` when `forward_keep`, placed **after** both the spam stage and the `X-Virus`
  check.

The ordering is load-bearing. RFC 5228 §4.4: `discard` cancels only the *implicit*
keep, not an explicit `redirect`. With the forward block above the virus check, an
infected message would be redirected onward and only the local copy dropped.

Why patched here rather than built from `master`: the fork's master is roughly five
years ahead of this image (`models.py` alone differs by 1923 lines, and master
carries an `sso/` package this tree does not have), so building from it would put
five years of unrelated change in front of all mail. The deployed `default.sieve`
and `resolve_destination` are functionally identical to master's for the parts being
changed, so the patch applies cleanly to this tree. The equivalent change on master
(`a72a2a2e`) carries unit tests for the spam-then-virus-then-redirect ordering.

Verified before deploy: the rendered sieve for all 18 forwarding users compiles
under `sievec` in the live imap pod — 18/18.

Image: `europe-west1-docker.pkg.dev/shared-199814/tools/mailu-admin:b6744e37-csrf1-sieve1`
Revert: re-pin `admin.yaml` to `weynwebworks/mailu-admin:b6744e37-csrf1`.
