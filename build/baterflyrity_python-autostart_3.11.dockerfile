
FROM baterflyrity/python-autostart:3.11

# TAG=3.11

LABEL author="baterflyrity"
LABEL mail="baterflyrity@yandex.ru"
LABEL home="https://github.com/baterflyrity/pythonssh"
LABEL version="1.1.0"
LABEL description="SSH server (sshd) container with user root and password 123. Comes with preinstalled python."

# see https://github.com/panubo/docker-sshd


# Install sshd
RUN apk update && \
    apk add bash git openssh rsync augeas shadow rssh && \
    deluser $(getent passwd 33 | cut -d: -f1) && \
    delgroup $(getent group 33 | cut -d: -f1) 2>/dev/null || true && \
    mkdir -p ~root/.ssh /etc/authorized_keys && chmod 700 ~root/.ssh/ && \
    augtool 'set /files/etc/ssh/sshd_config/AuthorizedKeysFile ".ssh/authorized_keys /etc/authorized_keys/%u"' && \
    echo -e "Port 22\n" >> /etc/ssh/sshd_config && \
    cp -a /etc/ssh /etc/ssh.cache && \
    rm -rf /var/cache/apk/*

# Run sshd on startup
COPY sshd.sh /sshd.sh
EXPOSE 22
ENV AUTOSTART_SSHD="/sshd.sh /usr/sbin/sshd -Def /etc/ssh/sshd_config"
# base image should be baterflyrity/python-autostart otherwise define ENTRYPOINT with command above
