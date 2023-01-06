FROM ubuntu:jammy

WORKDIR /opt

ARG SITE_ID=@SITE_ID@
ARG ARCHIVER_APPLIANCE_VERSION=@ARCHIVER_AP_VERSION@
ARG TIMEZONE=@TIMEZONE@
ARG JDBC_VER=@MARIADB_JDBC_VER@

ENV TOMCAT_HOME=/usr/share/tomcat9
ENV ANT_OPTS="-Dwardest=/opt/epicsarchiverap/wars -Dtomcathome=$TOMCAT_HOME -Darchapplsite=$SITE_ID"
ENV JAVA_OPTS="-XX:+UseG1GC -Xms@JAVA_MEMORY_LIMIT@ -Xmx@JAVA_MEMORY_LIMIT@ -ea -Dfile.encoding=UTF8 -Duser.timezone=$TIMEZONE"

ARG CONFIG_DIR=/opt/site-template/$SITE_ID/classpathfiles
ENV ARCHAPPL_APPLIANCES=$CONFIG_DIR/appliances.xml
ENV ARCHAPPL_MYIDENTITY=appliance0
ENV ARCHAPPL_POLICES=$CONFIG_DIR/polices.py
ENV ARCHAPPL_PROPERTIES_FILENAME=$CONFIG_DIR/archappl.properties
ENV ARCHAPPL_SHORT_TERM_FOLDER=/storage/sts
ENV ARCHAPPL_MEDIUM_TERM_FOLDER=/storage/mts
ENV ARCHAPPL_LONG_TERM_FOLDER=/storage/lts
ENV ARCHAPPL_ALL_APPS_ON_ONE_JVM="true"

RUN export EPICS_CA_ADDR_LIST=@EPICS_CA_ADDR_LIST@
RUN export EPICS_CA_AUTO_ADDR_LIST=@EPICS_CA_AUTO_ADDR_LIST@
RUN export EPICS_CA_MAX_ARRAY_BYTES=@EPICS_CA_MAX_ARRAY_BYTES@

RUN apt-get update \
    && apt-get install -y apt-utils wget git ant openjdk-17-jdk tomcat9 tomcat9-common tomcat9-admin tomcat9-user libtomcat9-java jsvc unzip vim iputils-ping iproute2 mariadb-client

# Download Archiver appliance and submodules
RUN git clone -b $ARCHIVER_APPLIANCE_VERSION https://github.com/slacmshankar/epicsarchiverap.git \
    && cd epicsarchiverap \
    && git submodule update --init --recursive

COPY site-template site-template

RUN wget https://downloads.mariadb.com/Connectors/java/connector-java-$JDBC_VER/mariadb-java-client-$JDBC_VER.jar \
    && mv mariadb-java-client-$JDBC_VER.jar $TOMCAT_HOME/lib/ \
    && chmod 755 $TOMCAT_HOME/lib/mariadb-java-client-$JDBC_VER.jar

# Build Archiver appliance
RUN mkdir -p /opt/epicsarchiverap/wars \
    && cp -rf /opt/site-template/$SITE_ID /opt/epicsarchiverap/src/sitespecific \
    && cd /opt/epicsarchiverap \
    && ant \
    && ant sitespecificbuild

# Install services
RUN mkdir -p /opt/epicsarchiverap/mgmt/conf \
    && mkdir -p /opt/epicsarchiverap/mgmt/webapps \
    && cp /opt/epicsarchiverap/wars/mgmt.war /opt/epicsarchiverap/mgmt/webapps \
    && cp $TOMCAT_HOME/skel/conf/* /opt/epicsarchiverap/mgmt/conf \
    && sed -i -e 's|Connector port="8080"|Connector port="17665"|g' /opt/epicsarchiverap/mgmt/conf/server.xml \
    && cp -f /opt/site-template/$SITE_ID/classpathfiles/context.xml /opt/epicsarchiverap/mgmt/conf/context.xml \
    && mkdir -p /opt/epicsarchiverap/engine/conf \
    && mkdir -p /opt/epicsarchiverap/engine/webapps \
    && cp /opt/epicsarchiverap/wars/engine.war /opt/epicsarchiverap/engine/webapps \
    && cp $TOMCAT_HOME/skel/conf/* /opt/epicsarchiverap/engine/conf \
    && sed -i -e 's|Connector port="8080"|Connector port="17666"|g' /opt/epicsarchiverap/engine/conf/server.xml \
    && cp -f /opt/site-template/$SITE_ID/classpathfiles/context.xml /opt/epicsarchiverap/engine/conf/context.xml \
    && mkdir -p /opt/epicsarchiverap/etl/conf \
    && mkdir -p /opt/epicsarchiverap/etl/webapps \
    && cp /opt/epicsarchiverap/wars/etl.war /opt/epicsarchiverap/etl/webapps \
    && cp $TOMCAT_HOME/skel/conf/* /opt/epicsarchiverap/etl/conf \
    && sed -i -e 's|Connector port="8080"|Connector port="17667"|g' /opt/epicsarchiverap/etl/conf/server.xml \
    && cp -f /opt/site-template/$SITE_ID/classpathfiles/context.xml /opt/epicsarchiverap/etl/conf/context.xml \
    && mkdir -p /opt/epicsarchiverap/retrieval/conf \
    && mkdir -p /opt/epicsarchiverap/retrieval/webapps \
    && cp /opt/epicsarchiverap/wars/retrieval.war /opt/epicsarchiverap/retrieval/webapps \
    && cp $TOMCAT_HOME/skel/conf/* /opt/epicsarchiverap/retrieval/conf \
    && sed -i -e 's|Connector port="8080"|Connector port="17668"|g' /opt/epicsarchiverap/retrieval/conf/server.xml \
    && cp -f /opt/site-template/$SITE_ID/classpathfiles/context.xml /opt/epicsarchiverap/retrieval/conf/context.xml


# Start services
ENTRYPOINT sleep 30 \
    && export CATALINA_BASE=/opt/epicsarchiverap/mgmt \
    && bash "$TOMCAT_HOME/bin/startup.sh" \
    && export CATALINA_BASE=/opt/epicsarchiverap/engine \
    && bash "$TOMCAT_HOME/bin/startup.sh" \
    && export CATALINA_BASE=/opt/epicsarchiverap/etl \
    && bash "$TOMCAT_HOME/bin/startup.sh" \
    && export CATALINA_BASE=/opt/epicsarchiverap/retrieval \
    && bash "$TOMCAT_HOME/bin/startup.sh" \
    && bash
