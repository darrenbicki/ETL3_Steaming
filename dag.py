from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import importlib

def print_version():
    mod = importlib.import_module('airflow.providers.google.cloud.operators.dataflow')
    print(dir(mod))

with DAG('check_google_provider', start_date=datetime(2025, 1, 1), schedule_interval=None, catchup=False) as dag:
    t = PythonOperator(task_id='check_import', python_callable=print_version)
