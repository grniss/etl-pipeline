# etl-pipeline [UNFINISHED]

This repository is purpose to create etl process to using airflow to execute sparksql for move data from postgresql to hive external table.

### There are some process broke and cannot just run compose command yet.

## Requirement

- Docker
- Docker compose > 2.0.0

Due to my limitation of knowledge, I didn't manage to configure spark to use `hive.metastore.uris"` as thrift uri in time

So I decided to work around by using hive-metastore built-in from Spark.

(I try to use jdbc connection but didn't manage to find way to convert/adpter write parquet file with jdbc connection too.)

The complete version of this architecture is aim to use hive without hadoop, since the requirement only needed external table and hadoop MapReduce + HDFS could be skip from my understand.

## Assumptions

- This hands-on architecture is to retreive data from postgresql and save to hive external table and export csv file
- Airflow task to insert further postgresql data is not in scope of this hands-on

## Component

- Spark
- Airflow
- Postgres

## How to run

For easily virtualization, chmod the folder inside this repo to enable output file in this folder

`chmod 666 ./resources/output`

`docker-compose up -d`

## If there are any problem please run

```
docker exec -u 0 sc-master-container chmod 777 /opt/bitnami/spark/output
docker exec -u 0 etl-pipeline-airflow-worker-1 chmod 777 /var/run/docker.sock
docker exec -u 0 etl-pipeline-airflow-webserver-1 chmod 777 /var/run/docker.sock
docker exec -u 0 etl-pipeline-airflow-triggerer-1 chmod 777 /var/run/docker.sock
docker exec -u 0 etl-pipeline-airflow-scheduler-1 chmod 777 /var/run/docker.sock
```

## How to test

- Enter postgres container

```
# Exec to database
docker exec -it pg-container psql -d temp -U temp
# Run SQL command to check
SELECT * FROM restaurant_detail LIMIT 5;
SELECT COUNT(*) FROM restaurant_detail;
SELECT * FROM order_detail LIMIT 5;
SELECT COUNT(*) FROM order_detail;
\d restaurant_detail
\d order_detail
# etc
\q
```

- Manual airflow execution
  - You can access airflow admin-ui by localhost:8080 and trigger `daily_dag` to execute pipeline
- Manual submit spark task
- Or you can directly submit spark task without enter airflow
  `docker exec sc-master-container /opt/bitnami/spark/bin/spark-submit --master local[*] --name etl /usr/local/spark/app/etl_pg_hive.py`
- Hive database (Note that it needed the first spark job execute first before database is initialize)

```
# Exec to pyspark cli
docker exec -it sc-master-container pyspark
# Acquire spark session
session = (SparkSession
        .builder
        .appName('etl-pg-hive')
        .enableHiveSupport()
        .config("spark.sql.parquet.writeLegacyFormat",True)\
        .getOrCreate()
)
# Run hive with sql command
session.sql("SELECT * FROM restaurant_detail LIMIT 5")
session.sql("SELECT * FROM restaurant_detail_new LIMIT 5")
session.sql("SELECT * FROM order_detail LIMIT 5")
session.sql("SELECT * FROM order_detail_new LIMIT 5")
session.sql("SELECT COUNT(*) FROM restaurant_detail")
session.sql("SELECT COUNT(*) FROM restaurant_detail_new")
session.sql("SELECT COUNT(*) FROM order_detail")
session.sql("SELECT COUNT(*) FROM order_detail_new")
# etc
exit()
```

- Output file
  - the output file would be placed at `resources/output`
- Change initial data
  - replace csv file at `build/postgres/raw`
  - rebuild postgres container by

```
docker-compose down postgres
docker-compose volume rm -f lmwn-data-engineer-hands-on_pgdata
docker-compose up -d postgres
```

- Reset hive database
  `docker exec sc-master-container /opt/bitnami/spark/bin/spark-submit --master local[*] --name etl /usr/local/spark/app/reset.py`

## Implementation detail/consideration

### Disclaimer: I haven't got literally knowledge in big data tool/architecture these details are only coming from my understand through document and this hands-on

- Postgres
  - Sqoop and Spark, I understand that sqoop is used for transfer data to HDFS and do MapReduce from there. So I think using spark which could transform data and JDBC to Postgres by itself is better.
- Hive
  - As I mentions above, I think that Hive is doesn't need MapReduce and HDFS so I tried to minimize size of application and reduce build time by skipped install hadoop
  - I have seen some architecture connect to hive via HDFS and process data. But I think that is slower since spark could use thrift server or jdbc.
  - Plenty of tried to use pyspark connect hive thrift server via thrift server but still got connection refused. However I could did netcat on thrift port so it may need more configure, which I couldn't manage to find.
  - Same to jdbc approach, I found method to read with spark, but didn't find appropriate way to write in parquet format yet (Think that it could be a driver to convert).
- Airflow with Spark
  - My docker-compose file using separate image of airflow and spark, there are some implementation that integrate those two together, but it look too heavy in my opinion. And this way may be more scalable since we doesn't that care network between airflow and spark.
  - However, this require harder attempt in configuration, I decided to choose exec docker approach since no time for SparkSubmitOperator way.

## Reference

- Hive without HDFS: https://funinit.wordpress.com/2020/12/08/how-to-start-apache-hive-without-hdfs/
