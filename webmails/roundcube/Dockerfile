# Roundcube 1.6 on Debian trixie + PHP from packages.sury.org (mod_php, prefork).
#
# Why not php:8.x-apache: on 2026-10-21 the official images were still on
# 8.3.35 / 8.4.26 (vulnerable to CVE-2026-109618/109619) while sury already
# shipped 8.3.36. The build refuses any PHP older than MIN_PHP_VERSION, so a
# rebuild can never silently go back to a vulnerable release.
FROM debian:trixie-20261020-slim

ARG VERSION
ARG PHP=8.3
ARG MIN_PHP_VERSION=8.3.36
ARG ROUNDCUBE_VERSION=1.6.20
ARG ROUNDCUBE_SHA256=46919c70c85609b57038903c4ecc4e1d7fa4e14c535fe5b14192d778dcd4a1ee
ARG CARDDAV_VERSION=5.1.4
ARG CARDDAV_SHA256=0ffa55ec6da5671d6c413a27d2511e903cd4e63de03c3e9480038844fa4625eb

ENV TZ=Etc/UTC \
    PHP_VERSION=${PHP} \
    DEBIAN_FRONTEND=noninteractive

LABEL version=$VERSION \
      org.opencontainers.image.title="mailu-roundcube" \
      roundcube.version=$ROUNDCUBE_VERSION \
      carddav.version=$CARDDAV_VERSION

RUN set -eu \
 && apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -fsSLo /tmp/sury.deb https://packages.sury.org/debsuryorg-archive-keyring.deb \
 && dpkg -i /tmp/sury.deb && rm /tmp/sury.deb \
 && echo "deb [signed-by=/usr/share/keyrings/debsuryorg-archive-keyring.gpg] https://packages.sury.org/php/ trixie main" \
      > /etc/apt/sources.list.d/php.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 libapache2-mod-php${PHP} \
      php${PHP}-cli php${PHP}-intl php${PHP}-mbstring php${PHP}-xml php${PHP}-zip \
      php${PHP}-gd php${PHP}-curl php${PHP}-mysql php${PHP}-pgsql php${PHP}-sqlite3 \
      php${PHP}-ldap php${PHP}-imagick php${PHP}-opcache \
      python3 python3-jinja2 gpg gpg-agent tzdata \
 && rm -rf /var/lib/apt/lists/* \
 && php -r "exit(version_compare(PHP_VERSION, '${MIN_PHP_VERSION}', '>=') ? 0 : 1);" \
    || { echo "PHP $(php -r 'echo PHP_VERSION;') < ${MIN_PHP_VERSION}: refusing to build" >&2; exit 1; }

# PHP settings shared by apache2 and cli. 99z-* is the CVE-2026-109618
# defense in depth: upload progress tracking is not used by Roundcube.
COPY php-hardening.ini /tmp/
RUN set -eu \
 && for sapi in apache2 cli; do \
      cp /tmp/php-hardening.ini /etc/php/${PHP}/${sapi}/conf.d/99z-cve-2026-109618.ini; \
      ln -sf /etc/php/${PHP}/roundcube.ini /etc/php/${PHP}/${sapi}/conf.d/90-roundcube.ini; \
    done \
 && rm /tmp/php-hardening.ini

# Apache: serve public_html only (config/, logs/, temp/ are not web-reachable),
# log to the container's stdout/stderr, skip local health probes in the access log.
COPY apache-roundcube.conf /etc/apache2/sites-available/000-default.conf
RUN set -eu \
 && a2enmod rewrite deflate expires headers \
 && a2disconf other-vhosts-access-log \
 && echo "ServerSignature Off\nServerTokens Prod\nServerName roundcube" >> /etc/apache2/apache2.conf \
 && ln -sfT /dev/stderr /var/log/apache2/error.log \
 && ln -sfT /dev/stdout /var/log/apache2/access.log

RUN set -eu \
 && rm -rf /var/www/html \
 && cd /var/www \
 && curl -fsSLo rc.tgz https://github.com/roundcube/roundcubemail/releases/download/${ROUNDCUBE_VERSION}/roundcubemail-${ROUNDCUBE_VERSION}-complete.tar.gz \
 && echo "${ROUNDCUBE_SHA256}  rc.tgz" | sha256sum -c - \
 && curl -fsSLo carddav.tgz https://github.com/mstilkerich/rcmcarddav/releases/download/v${CARDDAV_VERSION}/carddav-v${CARDDAV_VERSION}.tar.gz \
 && echo "${CARDDAV_SHA256}  carddav.tgz" | sha256sum -c - \
 && tar xzf rc.tgz && tar xzf carddav.tgz && rm rc.tgz carddav.tgz \
 && mv roundcubemail-${ROUNDCUBE_VERSION} html \
 && mv carddav html/plugins/ \
 && cd html \
 && rm -rf CHANGELOG.md SECURITY.md INSTALL LICENSE README.md UPGRADING composer.json-dist installer \
 && rm -rf plugins/autologon plugins/example_addressbook plugins/http_authentication plugins/krb_authentication \
           plugins/squirrelmail_usercopy plugins/virtuser_file plugins/virtuser_query \
 && chown -R root:root . \
 && chown www-data:www-data logs temp \
 && chmod -R a+rX .

COPY mailu.php /var/www/html/plugins/mailu/mailu.php
COPY config.inc.php config.inc.carddav.php php.ini start.py healthcheck.sh /

EXPOSE 80/tcp
VOLUME /data
VOLUME /overrides

CMD ["/start.py"]

HEALTHCHECK CMD /healthcheck.sh

RUN echo $VERSION >> /version
