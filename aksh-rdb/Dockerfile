FROM postgres:13.2-alpine

RUN apk add openssl

WORKDIR /var/lib/postgresql/
USER postgres
RUN openssl req -new -text -passout pass:abcd -subj /CN=localhost -out server.req -keyout privkey.pem
RUN openssl rsa -in privkey.pem -passin pass:abcd -out server.key
RUN openssl req -x509 -in server.req -text -days 3650 -key server.key -out server.crt
RUN chmod og-rwx server.key

WORKDIR /
USER root

CMD docker-entrypoint.sh -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key
