CREATE USER airflow WITH PASSWORD 'airflow';

CREATE DATABASE airflow;

GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

CREATE USER temp WITH PASSWORD 'temp_password';

CREATE DATABASE temp;

\c temp;

DROP TABLE IF EXISTS order_detail;

CREATE TABLE order_detail(
    order_created_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL,
    price INT NOT NULL,
    discount FLOAT(1),
    id VARCHAR(36) PRIMARY KEY,
    driver_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    restaurant_id VARCHAR(10)
);

CREATE INDEX order_created_timestamp_idx ON order_detail USING btree (order_created_timestamp);

ALTER TABLE
    order_detail CLUSTER ON order_created_timestamp_idx;

COPY order_detail
FROM
    '/var/data/raw/order_detail.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS restaurant_detail;

CREATE TABLE restaurant_detail(
    id VARCHAR(10) PRIMARY KEY,
    restaurant_name VARCHAR(60) NOT NULL,
    category VARCHAR(30) NOT NULL,
    estimated_cooking_time FLOAT(1) NOT NULL,
    latitude DECIMAL(11, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL
);

COPY restaurant_detail
FROM
    '/var/data/raw/restaurant_detail.csv' DELIMITER ',' CSV HEADER;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to temp;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to temp;

GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to temp;