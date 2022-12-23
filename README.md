# Dockerfiles for EPICS Archiver Appliance
[EPICS Archiver Appliance](https://github.com/slacmshankar/epicsarchiverap) save [EPICS](https://github.com/epics-base/epics-base) PVs to a database and provide a web interface to view the data. A docker script was created to automate Archiver installation, making it easy to build a small archiver. Rather than building it locally, it is expected to be advantageous in terms of memory resource management.

## Usage

### Pre-requisites
* Install latest Docker
```bash
# Example Ubuntu 20.04
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor
-o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture)
  signed-by=/etc/apt/keyrings/docker.gpg]
  https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
    > /dev/null
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
Tested on docker(20.10.22) and docker-compose(v2.14.1)

* Docker network create
```bash
docker network create \
--driver=bridge \
--subnet=10.2.0.0/24 \
--gateway=10.2.0.1 \
docker1
```
* [Manage docker as a non-root
  user](https://docs.docker.com/engine/install/linux-postinstall/)
```bash
# Create the docker group
sudo groupadd docker
# Add your user to the docker group
sudo usermod -aG docker $USER
# Logout and login
```

### Build
* Make site specific settings
```bash
cp -r ./archiver-ap/site-template/pls ./archiver-ap/site-template/$SITE_ID
```
* Edit [CONFIG_ENV](configure/CONFIG_ENV)
* Build docker images
```bash
make
```
* Edit /etc/hosts
```bash
10.2.0.9 archiver-ap
10.2.0.10 archiver-db
IOC_IP sr-ioc
```

### Run
```bash
make start
```

### Web
```bash
firefox http://archiver-ap:17665/mgmt/ui/index.html
```

## Reference
* [epicsarchiverap-env](https://github.com/jeonghanlee/epicsarchiverap-env)
* [docker-archiver-appliance](https://eicweb.phy.anl.gov/controls/epics/archiver/docker-archiver-appliance)
* [EPICS Archiver Appliance WIKI](https://github.com/slacmshankar/epicsarchiverap/wiki/setup_rhel7_rpms)

