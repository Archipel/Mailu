# "imapsieve" is required for the imap.user environment item: without it
# ${user} is empty and the allowlist hook calls .../remove/ (404, 2026-11-20).
require ["vnd.dovecot.execute", "imap4flags", "imapsieve", "environment", "variables"];

if environment :matches "imap.user" "*" {
  set "user" "${1}";
}

setflag "\\seen";
execute :pipe "spam" ["${user}"];
