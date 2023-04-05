# Python SSH

SSH server (sshd) docker images pack with user **root** and password **123**.

Each container contains preinstalled python with tag version, e.g. *baterflyrity/pythonssh:3.11* = *python:3.11* + sshd.

# Usage example

Start container and connect to it via ssh (wait for several seconds to let server self-configure):
```bash
docker run -itd --rm -p 12345:22/tcp --name pythonssh baterflyrity/pythonssh
# wait for self-configuration
ssh root@localhost -p 12345 # password is 123
```

then via ssh interactive session in container

```bash
python3 -V
pip3 list
```

container will be deleted automatically (option `--rm`) on exit. One can force container to exit with:

```bash
docker stop pythonssh
```

---

Alternatively just start ssh server in container and run some commads:
```bash
docker run -itd --rm -p 12345:22/tcp --name pythonssh baterflyrity/pythonssh  
# wait for self-configuration
ssh root@localhost -p 12345 python3 -V && pip3 list # password is 123
# delete server after done
docker stop pythonssh
```

# Building from sources

Requirements:

* docker
* python3.11
* git

```bash
git clone https://github.com/baterflyrity/pythonssh
cd  pythonssh
python3.11 -m pip install -r requirements.txt
python3.11 builder.py make --password 123 --image baterflyrity/python-autostart:latest --image baterflyrity/python-autostart:alpine --image baterflyrity/python-autostart:3.8 --image baterflyrity/python-autostart:3.9 --image baterflyrity/python-autostart:3.10 --image baterflyrity/python-autostart:3.11
python3.11 builder.py build --user baterflyrity # insert your username
# optionally upload to dockerhub
python3.11 builder.py push
```

# See also

* [baterflyrity/python-autostart](https://hub.docker.com/r/baterflyrity/python-autostart) - docker image with custom autostart commands and preinstalled python.

# Changelog

**1.1.0**
 * Migrate to [baterflyrity/python-autostart](https://hub.docker.com/r/baterflyrity/python-autostart) base images to simplify sshd autostart.
 * Update examples.
