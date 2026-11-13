require "variables";
require "vacation";
require "fileinto";
require "envelope";
require "mailbox";
require "imap4flags";
require "regex";
require "relational";
require "date";
require "comparator-i;ascii-numeric";
require "spamtestplus";
require "editheader";
require "index";

if header :index 2 :matches "Received" "from * by * for <*>; *"
{
  deleteheader "Delivered-To";
  addheader "Delivered-To" "<${3}>";
}

{% if user.spam_enabled %}
{#- Per-user allowlist: never file an allowlisted sender into Junk, but only
    when rspamd's own DMARC check passed. X-Mailu-DMARC is set by rspamd
    (milter_headers.conf, custom routine) after removing any copy the message
    arrived with; it must not be read from Authentication-Results, whose spf
    clause quotes the sender-controlled envelope sender. Entries are validated
    in User.normalize_allowlist_entry, so they cannot break out of a string. #}
{%- set allow_addresses = user.spam_allowlist_addresses %}
{%- set allow_domains = user.spam_allowlist_domains %}
{%- if allow_addresses or allow_domains %}
if allof(header :matches "X-Mailu-DMARC" "pass *",
         anyof({%- if allow_addresses %}address :is :all "from" [{% for a in allow_addresses %}"{{ a }}"{{ ", " if not loop.last }}{% endfor %}]{% endif %}
               {%- if allow_addresses and allow_domains %},
               {% endif %}{%- if allow_domains %}address :is :domain "from" [{% for d in allow_domains %}"{{ d }}"{{ ", " if not loop.last }}{% endfor %}]{% endif %}))
{
  set "spam_allowlisted" "1";
  addheader "X-Mailu-Allowlisted" "yes";
}
{%- endif %}

if allof(not string :is "${spam_allowlisted}" "1",
         spamtest :percent :value "gt" :comparator "i;ascii-numeric" "{{ user.spam_threshold }}")
{
  setflag "\\seen";
  fileinto :create "Junk";
  stop;
}
{% endif %}
if exists "X-Virus" {
  discard;
  stop;
}

{# Forwarding runs AFTER the virus check, and the ordering is load-bearing.
   RFC 5228 4.4: `discard` cancels only the IMPLICIT keep -- it does not cancel
   an explicit `redirect`. With this block placed earlier, an infected message
   would be relayed on to the external destination and only the local copy
   dropped, which is precisely the "we relay other people's poison under our own
   IP" problem this whole change exists to stop. #}
{% if user.forward_enabled %}
{% for destination in user.forward_destination %}
redirect "{{ destination }}";
{% endfor %}
{% if user.forward_keep %}keep;{% endif %}
{% endif %}

{% if user.reply_active %}
vacation :days 1 {% if user.displayed_name != "" %}:from "{{ user.displayed_name }} <{{ user.email }}>"{% endif %} :subject "{{ user.reply_subject }}" "{{ user.reply_body }}";
{% endif %}
