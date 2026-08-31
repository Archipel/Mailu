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
if spamtest :percent :value "gt" :comparator "i;ascii-numeric" "{{ user.spam_threshold }}"
{
  setflag "\\seen";
  fileinto :create "Junk";
  stop;
}
{% endif %}
{% if user.forward_enabled %}
{% for destination in user.forward_destination %}
redirect "{{ destination }}";
{% endfor %}
{% if user.forward_keep %}keep;{% endif %}
{% endif %}

if exists "X-Virus" {
  discard;
  stop;
}

{% if user.reply_active %}
vacation :days 1 {% if user.displayed_name != "" %}:from "{{ user.displayed_name }} <{{ user.email }}>"{% endif %} :subject "{{ user.reply_subject }}" "{{ user.reply_body }}";
{% endif %}
