require ["vnd.dovecot.execute", "imap4flags", "environment", "variables"];

if environment :matches "imap.user" "*" {
  set "user" "${1}";
}

setflag "\\seen";
execute :pipe "spam" ["${user}"];
