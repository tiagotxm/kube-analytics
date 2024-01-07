from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

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
    description='Download and show customers data',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:

    hello_world_task = KubernetesPodOperator(
        task_id='download_customers_data',
        namespace='airflow',
        image="tiagotxm/customer-gz-loader",
        # cmds=["echo"],
        # arguments=["Hello, World!"],
        name="customers-data",
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod"
    )
