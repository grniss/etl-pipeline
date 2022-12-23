from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'grniss',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_dag',
    default_args = default_args,
    description = 'daily dag to update data from csv to postgres and to hive external table',
    start_date = days_ago(1),
    schedule_interval = timedelta(days=1)
)

submit = BashOperator(
    task_id='submit_etl_pg_to_hive',
    bash_command='docker exec sc-master-container /opt/bitnami/spark/bin/spark-submit --master local[*] --name etl /usr/local/spark/app/etl_pg_hive.py',
    dag=dag,
)

submit