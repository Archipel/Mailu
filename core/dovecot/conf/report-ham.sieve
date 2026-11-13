require ["vnd.dovecot.execute", "copy", "imapsieve", "environment", "variables"];

if environment :matches "imap.mailbox" "*" {
  set "mailbox" "${1}";
}

if environment :matches "imap.user" "*" {
  set "user" "${1}";
}

if string "${mailbox}" "Trash" {
  stop;
}

execute :pipe "ham" ["${user}"];
