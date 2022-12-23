DROP TABLE IF EXISTS order_detail;

CREATE EXTERNAL TABLE IF NOT EXISTS order_detail (
    order_created_timestamp TIMESTAMP,
    status VARCHAR(30),
    price INT,
    discount FLOAT,
    id VARCHAR(36),
    driver_id VARCHAR(36),
    user_id VARCHAR(36),
    restaurant_id VARCHAR(10)
) PARTITIONED BY (dt VARCHAR(8)) STORED AS PARQUET LOCATION '/spark/order_detail';

DROP TABLE IF EXISTS restaurant_detail;

CREATE EXTERNAL TABLE IF NOT EXISTS restaurant_detail (
    id VARCHAR(10),
    restaurant_name VARCHAR(60),
    category VARCHAR(30),
    estimated_cooking_time FLOAT,
    latitude DECIMAL(11, 8),
    longitude DECIMAL(11, 8)
) PARTITIONED BY (dt STRING) STORED AS PARQUET LOCATION '/spark/restaurant_detail';

DROP TABLE IF EXISTS order_detail_new;

CREATE EXTERNAL TABLE IF NOT EXISTS order_detail_new (
    order_created_timestamp TIMESTAMP,
    status VARCHAR(30),
    price INT,
    discount FLOAT,
    id VARCHAR(36),
    driver_id VARCHAR(36),
    user_id VARCHAR(36),
    restaurant_id VARCHAR(10),
    discount_no_null FLOAT
) PARTITIONED BY (dt STRING) STORED AS PARQUET LOCATION '/spark/order_detail_new';

DROP TABLE IF EXISTS restaurant_detail_new;

CREATE EXTERNAL TABLE IF NOT EXISTS restaurant_detail_new (
    id VARCHAR(10),
    restaurant_name VARCHAR(60),
    category VARCHAR(30),
    estimated_cooking_time FLOAT,
    latitude DECIMAL(11, 8),
    longitude DECIMAL(11, 8),
    cooking_bin VARCHAR(1)
) PARTITIONED BY (dt STRING) STORED AS PARQUET LOCATION '/spark/restaurant_detail_new';