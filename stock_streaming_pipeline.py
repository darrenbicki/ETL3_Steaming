from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from datetime import timedelta
import os

# Defaults
PROJECT_ID = os.environ.get("project_id", "steel-bridge-466914-e0")
REGION = os.environ.get("region", "us-central1")

DATAFLOW_BUCKET = "gs://bkt-stock"
DATAFLOW_PY_FILE = f"{DATAFLOW_BUCKET}/dataflow_job.py"
PUBSUB_TOPIC = f"projects/{PROJECT_ID}/topics/stock_prices"
BIGQUERY_TABLE = f"{PROJECT_ID}:stock_data.stock_prices_agg"

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=15),
}

with DAG(
    dag_id='stock_streaming_pipeline',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
    tags=['dataflow', 'streaming', 'bq'],
) as dag:

    # Publish stock data into Pub/Sub via Cloud Function
    publish_stock_data = HttpOperator(
        task_id='publish_stock_data',
        method='GET',
        http_conn_id='cloud_function_default',
        endpoint='publish_stock_data',
        response_check=lambda response: response.status_code == 200,
        log_response=True,
        retries=3,
        retry_delay=timedelta(minutes=1)
    )

    # Launch Apache Beam pipeline on Dataflow
    run_dataflow = DataflowCreatePythonJobOperator(
        task_id="run_dataflow",
        py_file=DATAFLOW_PY_FILE,
        py_options=[],
        options={
            "project": PROJECT_ID,
            "region": REGION,
            "streaming": True,
            "input_topic": PUBSUB_TOPIC,
            "output_table": BIGQUERY_TABLE,
            "temp_location": f"{DATAFLOW_BUCKET}/temp",
            "staging_location": f"{DATAFLOW_BUCKET}/staging",
            "job_name": "stock-pipeline-{{ ts_nodash }}",
        },
        location=REGION,
    )

    # Validate results in BigQuery
    check_bq = BigQueryCheckOperator(
        task_id='check_bigquery',
        sql=f"""
            SELECT COUNT(*) 
            FROM `{PROJECT_ID}.stock_data.stock_prices_agg`
            WHERE window_end > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
        """,
        use_legacy_sql=False,
    )

    # DAG flow: publish → run Dataflow → validate in BigQuery
    publish_stock_data >> run_dataflow >> check_bq
