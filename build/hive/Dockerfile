FROM debian:buster-slim as downloader

ARG JENKINS_VERSION
WORKDIR /usr/bin/downloader
ADD https://dlcdn.apache.org/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz .
ADD https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz .

FROM ubuntu:20.04

WORKDIR /usr/bin/hive-wout-hdfs

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HIVE_HOME=/usr/bin/hive-wout-hdfs/apache-hive-3.1.3-bin
ENV PATH=$HIVE_HOME/bin:$PATH
ENV HADOOP_HOME=/usr/bin/hive-wout-hdfs/hadoop-3.3.4
ENV PATH=$HADOOP_HOME/bin:$PATH
ENV HIVE_OPTS="-hiveconf mapred.job.tracker=local \
    -hiveconf fs.default.name=file:///usr/bin/hive-wout-hdfs/tmp \
    -hiveconf hive.metastore.warehouse.dir=file:///usr/bin/hive-wout-hdfs/tmp/warehouse \
    -hiveconf javax.jdo.option.ConnectionURL=jdbc:derby:;databaseName=/usr/bin/hive-wout-hdfs/tmp/metastore_db;create=true"

COPY --from=downloader /usr/bin/downloader/apache-hive-3.1.3-bin.tar.gz /usr/bin/hive-wout-hdfs/
COPY --from=downloader /usr/bin/downloader/hadoop-3.3.4.tar.gz /usr/bin/hive-wout-hdfs/

RUN \
    apt update && \
    tar -xf apache-hive-3.1.3-bin.tar.gz && \
    tar -xf hadoop-3.3.4.tar.gz && \
    rm -rf apache-hive-3.1.3-bin.tar.gz && \
    rm -rf hadoop-3.3.4/hadoop-3.3.4.tar.gz && \
    apt-cache search openjdk- && \
    apt install -y openjdk-8-jdk-headless && \
    hive -e "show databases;" ; \
    cd tmp && rm -rf metastore_db && \
    schematool -initSchema -dbType derby && \
    exit 0;

COPY init.hql .
RUN hive -f init.hql

CMD [ "hiveserver2" ]
