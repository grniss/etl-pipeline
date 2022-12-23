FROM bitnami/spark:3.2.1

COPY postgresql-42.5.1.jar ./jars
# COPY hive-site.xml $HOME_SPARK/conf/

RUN mkdir /opt/bitnami/spark/output
RUN chmod 777 /opt/bitnami/spark/output
