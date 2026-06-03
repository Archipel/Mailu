ARG DISTRO=alpine:3.14.5

FROM $DISTRO
ARG VERSION

ENV TZ Etc/UTC

LABEL version=$VERSION

# python3 shared with most images
RUN apk add --no-cache \
    python3 py3-pip git bash py3-multidict py3-yarl tzdata \
  && pip3 install --upgrade pip

# Shared layer between nginx, dovecot, postfix, postgresql, rspamd, unbound, rainloop, roundcube
RUN pip3 install socrate==0.2.0

# Shared layer between dovecot and postfix
RUN pip3 install "podop>0.2.5"

# Image specific layers under this line
# Building pycares from source requires py3-wheel and libffi-dev packages
RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev py3-wheel libffi-dev \
  && pip3 install --no-binary :all: postfix-mta-sts-resolver==1.0.1 \
  && apk del .build-deps

# postfix-mysql: required by the SENDER_DEPENDENT_* mysql maps. It was present
# in the deployed image but never committed here — without it postfix
# temp-rejects all inbound with "unsupported dictionary type: mysql".
# cyrus-sasl: sasldb2 backend for smtpd inbound SASL auth (used by dovecot
# sieve redirect to authenticate as the sieve relay user on port 10025)
RUN apk add --no-cache postfix postfix-mysql postfix-pcre \
    cyrus-sasl cyrus-sasl-login cyrus-sasl-crammd5 \
    rsyslog logrotate

COPY conf /conf
# Cyrus SASL config for smtpd — sasldb2 is populated at startup by start.py
# from SIEVE_SMTP_AUTH_USER / SIEVE_SMTP_AUTH_PASSWORD env vars.
RUN mkdir -p /etc/sasl2 && cp /conf/sasl/smtpd.conf /etc/sasl2/smtpd.conf
COPY start.py /start.py

EXPOSE 25/tcp 10025/tcp
VOLUME ["/queue"]

CMD /start.py

HEALTHCHECK --start-period=350s CMD echo QUIT|nc localhost 25|grep "220 .* ESMTP Postfix"
RUN echo $VERSION >> /version
