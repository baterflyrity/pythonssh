# PythonSsh

SSH server (sshd) images pack with user **root** and password **123**.

Each container contains preinstalled python with tag version, e.g. *baterflyrity/pythonssh:3.11* = *python:3.11* + sshd. 

*:alpine* image does not include python.

### Usage example
```bash
docker run -d --rm -p 12345:22/tcp --name pythonssh baterflyrity/pythonssh:3.11
ssh root@localhost -p 12345 # password is 123
```
then via ssh session in container
```bash
python3.11 -V
pip3.11 list
```
container will be deleted automatically (option `--rm`) on exit. One can force container to exit with:
```bash
docker stop pythonssh
```

# Building from sources

Requirements:

* docker
* python3.11
* git

```bash
python3.11 -m pip install typer[all]
git clone https://github.com/baterflyrity/pythonssh.git
cd  pythonssh
python3.11 builder make --image python:3.11-alpine --image python:3.10-alpine --password 123 # insert non-default root password
python3.11 builder build --name "user/pythonssh" # insert your username
# optionally upload to dockerhub
python3.11 builder push --name "user/pythonssh" # insert your username

```
