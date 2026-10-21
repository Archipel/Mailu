#!/bin/sh
# Local liveness probe: the login page must render (the mailu plugin answers
# "OK" itself for this User-Agent when it is enabled).
exec curl -fsS -o /dev/null -H 'User-Agent: health' http://127.0.0.1/
