from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.operators.kubernetes_pod import KubernetesPodOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple Hello World DAG',
    schedule_interval=timedelta(days=1),
) as dag:

    hello_world_task = KubernetesPodOperator(
        task_id='hello_world_task',
        namespace='default',
        image="alpine:latest",
        cmds=["echo"],
        arguments=["Hello, World!"],
        name="hello-world-pod",
        in_cluster=True,
        get_logs=True
    )
