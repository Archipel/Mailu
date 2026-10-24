<?php
// Rendered by /start.py at container start.

// Scheme for storing the CardDAV passwords, in order from least to best security.
// Options: plain, base64, des_key, encrypted (default)
// "encrypted" uses the user's IMAP password, which the Mailu SSO token is not,
// so SSO setups must fall back to des_key.
$prefs['_GLOBAL']['pwstore_scheme'] = '{{ "des_key" if SSO else "encrypted" }}';

$prefs['_GLOBAL']['loglevel'] = \Psr\Log\LogLevel::WARNING;
$prefs['_GLOBAL']['loglevel_http'] = \Psr\Log\LogLevel::ERROR;
