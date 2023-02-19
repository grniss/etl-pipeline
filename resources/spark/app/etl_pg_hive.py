from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, date_format, lit, when
from pyspark.sql.types import IntegerType, FloatType, DecimalType

session = (SparkSession
        .builder
        .appName('etl-pg-hive')
        .enableHiveSupport()
        .config("spark.sql.parquet.writeLegacyFormat",True)
        .master("spark://spark-master:7077")
        .getOrCreate()
)

scripts = [
    "CREATE EXTERNAL TABLE IF NOT EXISTS order_detail ( order_created_timestamp TIMESTAMP, status VARCHAR(30), price INT, discount FLOAT, id VARCHAR(36), driver_id VARCHAR(36), user_id VARCHAR(36), restaurant_id VARCHAR(10)) PARTITIONED BY (dt VARCHAR(8)) STORED AS PARQUET LOCATION '/opt/bitnami/spark/temp/spark-warehouse/order_detail';",
    "CREATE EXTERNAL TABLE IF NOT EXISTS restaurant_detail ( id VARCHAR(10), restaurant_name VARCHAR(60), category VARCHAR(30), estimated_cooking_time FLOAT, latitude DECIMAL(11, 8), longitude DECIMAL(11, 8)) PARTITIONED BY (dt STRING) STORED AS PARQUET LOCATION '/opt/bitnami/spark/temp/spark-warehouse/restaurant_detail';",
]


for script in scripts:
    session.sql(script)


order_detail = session.read.jdbc(url="jdbc:postgresql://pg-container:5432/temp?user=temp&password=temp_password&sslenable=false", table="order_detail")
order_detail = order_detail.withColumn("order_created_timestamp", to_timestamp("order_created_timestamp"))
order_detail = order_detail.withColumn("price", col("price").cast(IntegerType()))
order_detail = order_detail.withColumn("discount", col("discount").cast(FloatType()))
order_detail = order_detail.withColumn("dt", date_format("order_created_timestamp", "yyyyMMdd"))
order_detail.write.mode("overwrite").format("parquet").insertInto("order_detail")


order_detail_new = order_detail
order_detail_new = order_detail.withColumn("discount_no_null", col("discount").cast("float"))
order_detail_new = order_detail_new.na.fill({"discount_no_null":0.0})
order_detail_new.write.partitionBy("dt").mode("overwrite").format("parquet").saveAsTable("order_detail_new")


restaurant_detail = session.read.jdbc(url="jdbc:postgresql://pg-container:5432/temp?user=temp&password=temp_password&sslenable=false", table="restaurant_detail")
restaurant_detail = restaurant_detail.withColumn("estimated_cooking_time", col("estimated_cooking_time").cast(FloatType()))
restaurant_detail = restaurant_detail.withColumn("latitude", col("latitude").cast(DecimalType(11,8)))
restaurant_detail = restaurant_detail.withColumn("longitude", col("longitude").cast(DecimalType(11,8)))
restaurant_detail = restaurant_detail.withColumn("dt", lit("latest"))
restaurant_detail.write.mode("overwrite").format("parquet").insertInto("restaurant_detail")


restaurant_detail_new = restaurant_detail.withColumn("cooking_bin",
                    when(col("estimated_cooking_time") <= 40, 1 )
                    .otherwise(when(col("estimated_cooking_time") <= 80, 2 ) 
                    .otherwise(when( col("estimated_cooking_time") <= 120, 3 )
                    .otherwise(lit(4)))))
restaurant_detail_new.write.partitionBy("dt").mode("overwrite").format("parquet").saveAsTable("restaurant_detail_new")

import os
import glob
import shutil

discount = order_detail_new \
                .join(restaurant_detail_new, order_detail_new.restaurant_id == restaurant_detail.id, "left") \
                .groupBy("category") \
                .avg("discount_no_null")             
discount.coalesce(1) \
   .write.format("com.databricks.spark.csv") \
   .option("header", "true") \
   .mode("overwrite") \
   .save("output/discount")

discount_csv = glob.glob("output/discount/*.csv")[0]
os.rename(discount_csv, "output/discount.csv")
shutil.rmtree("output/discount")

cooking = restaurant_detail_new.groupBy("cooking_bin").count()
cooking.coalesce(1) \
   .write.format("com.databricks.spark.csv") \
   .option("header", "true") \
   .mode("overwrite") \
   .save("output/cooking")

cooking_csv = glob.glob("output/cooking/*.csv")[0]
os.rename(cooking_csv, "output/cooking.csv")
shutil.rmtree("output/cooking")

session.stop()
