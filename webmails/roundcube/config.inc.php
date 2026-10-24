<?php
// Rendered by /start.py at container start. Do not edit in the container.

$config = array();

// Generals
$config['db_dsnw'] = {{ DB_DSNW | php }};
$config['temp_dir'] = '/tmp/';
$config['des_key'] = {{ DES_KEY | php }};
$config['cipher_method'] = 'AES-256-CBC';
$config['identities_level'] = 0;
$config['reply_all_mode'] = 1;
$config['log_driver'] = 'stdout';
$config['zipdownload_selection'] = true;
{%- if SESSION_TIMEOUT_MINUTES %}
$config['session_lifetime'] = {{ SESSION_TIMEOUT_MINUTES | int }};
{%- endif %}

// Mail servers (Roundcube >= 1.6: host:port, no separate *_port options)
$config['imap_host'] = {{ ((FRONT_ADDRESS or "front") ~ ":10143") | php }};
$config['smtp_host'] = {{ ((FRONT_ADDRESS or "front") ~ ":10025") | php }};
$config['smtp_user'] = '%u';
$config['smtp_pass'] = '%p';

// Sieve script management
$config['managesieve_host'] = {{ (IMAP_ADDRESS or "imap") | php }};
$config['managesieve_usetls'] = false;

// We access the IMAP and SMTP servers locally with internal names, SSL
// will obviously fail but this sounds better than allowing insecure login
// from the outer world
$ssl_no_check = array(
 'ssl' => array(
     'verify_peer' => false,
     'verify_peer_name' => false,
  ),
);
$config['imap_conn_options'] = $ssl_no_check;
$config['smtp_conn_options'] = $ssl_no_check;
$config['managesieve_conn_options'] = $ssl_no_check;

// roundcube customization
$config['product_name'] = 'Mailu Webmail';
$config['plugins'] = array({{ PLUGINS }});
{%- if SSO %}

// configure mailu sso plugin (needs a front that sets X-Remote-User*)
{%- if ADMIN and WEB_ADMIN %}
$config['support_url'] = {{ ("../.." ~ WEB_ADMIN) | php }};
{%- endif %}
$config['sso_logout_url'] = '/sso/logout';
{%- endif %}

// skin name: folder from skins/
$config['skin'] = 'elastic';

// configure enigma gpg plugin
$config['enigma_pgp_homedir'] = '/data/gpg';

// set From header for DKIM signed message delivery reports
$config['mdn_use_from'] = true;

// includes
{%- for inc in INCLUDES %}
include('/overrides/{{ inc }}');
{%- endfor %}
