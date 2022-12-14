# Dockerfiles for EPICS Archiver Appliance
[EPICS Archiver Appliance](https://github.com/slacmshankar/epicsarchiverap) save [EPICS](https://github.com/epics-base/epics-base) PVs to a database and provide a web interface to view the data. A docker script was created to automate Archiver installation, making it easy to build a small archiver. Rather than building it locally, it is expected to be advantageous in terms of memory resource management.

## Usage

### Pre-requisites
* [Install latest Docker](https://docs.docker.com/engine/install/ubuntu/)
    * Tested on docker(20.10.22) and docker-compose(v2.14.1)

* Docker daemon settings
```json
{
    "iptables" : false,
    "bip" : "10.1.1.1/24",
    "fixed-cidr" : "10.1.1.0/25",
    "default-address-pool": [
        {
            "base":"10.2.0.0/16",
            "size":24
        }
    ]
}
```

* Docker network create
```bash
docker network create \
--driver=bridge \
--subnet=10.2.0.0/24 \
--gateway=10.2.0.1 \
docker1
```

* Iptables for container network
```bash
*nat
:POSTROUTING ACCEPT [0:0]
-A POSTROUTING -o $IFACE -j MASQUERADE
-A POSTROUTING -o docker0 -j MASQUERADE
-A POSTROUTING -o docker1 -j MASQUERADE
COMMIT
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

* Edit /etc/hosts
```bash
10.2.0.9 archiver-ap
10.2.0.10 archiver-db
IOC_IP sr-ioc
```

### Build
* Make site specific settings
```bash
cp -r ./archiver-ap/site-template/pls ./archiver-ap/site-template/$SITE_ID
```
* Edit [CONFIG_ENV](configure/CONFIG_ENV)
    - use double quote for EPICS_CA_ADDR_LIST. ex) "192.168.0.1 192.168.0.2 192.168.0.3"
    - [routers will often not forward broadcast requests, which suggests using
      specific IP
      addresses.](https://epics-controls.org/resources-and-support/documents/howto-documents/configure-channel-access/)
    - Consider [using
      iptables](https://epics-controls.org/resources-and-support/documents/howto-documents/channel-access-reach-multiple-soft-iocs-linux/)
      if there are multiple IOCs.
* Build docker images
```bash
make
```

### Run
```bash
make start
```

### Web
```bash
firefox http://archiver-ap:17665/mgmt/ui/index.html
```

### Systemd

```bash
mkdir /etc/docker-compose
ln -s /opt/docker-epicsarchiverappliance /etc/docker-compose/archiverap

cat /etc/systemd/system/docker-compose@.service

[Unit]
Description=%i service with docker compose
PartOf=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/etc/docker-compose/%i
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target

systemctl start docker-compose@archiverap
```

## Reference
* [epicsarchiverap-env](https://github.com/jeonghanlee/epicsarchiverap-env)
* [docker-archiver-appliance](https://eicweb.phy.anl.gov/controls/epics/archiver/docker-archiver-appliance)
* [EPICS Archiver Appliance WIKI](https://github.com/slacmshankar/epicsarchiverap/wiki/setup_rhel7_rpms)

