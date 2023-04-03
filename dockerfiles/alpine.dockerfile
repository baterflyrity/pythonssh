FROM alpine

# TAG=alpine

LABEL author="baterflyrity"
LABEL mail="baterflyrity@yandex.ru"
LABEL home="https://github.com/baterflyrity/pythonssh"
LABEL version="1.0.0"
LABEL description="SSH server (sshd) container with user root and password 123."

# see https://github.com/panubo/docker-sshd
RUN apk update && \
    apk add bash git openssh rsync augeas shadow rssh && \
    deluser $(getent passwd 33 | cut -d: -f1) && \
    delgroup $(getent group 33 | cut -d: -f1) 2>/dev/null || true && \
    mkdir -p ~root/.ssh /etc/authorized_keys && chmod 700 ~root/.ssh/ && \
    augtool 'set /files/etc/ssh/sshd_config/AuthorizedKeysFile ".ssh/authorized_keys /etc/authorized_keys/%u"' && \
    echo -e "Port 22\n" >> /etc/ssh/sshd_config && \
    cp -a /etc/ssh /etc/ssh.cache && \
    rm -rf /var/cache/apk/*

# add user root with password 123 to login via ssh
ENV SSH_ENABLE_ROOT=true
ENV SSH_ENABLE_PASSWORD_AUTH=true
ENV SSH_ENABLE_ROOT_PASSWORD_AUTH=true
COPY setpasswd.sh /etc/entrypoint.d/setpasswd.sh

EXPOSE 22

COPY entry.sh /entry.sh

ENTRYPOINT ["/entry.sh"]

CMD ["/usr/sbin/sshd", "-D", "-e", "-f", "/etc/ssh/sshd_config"]
