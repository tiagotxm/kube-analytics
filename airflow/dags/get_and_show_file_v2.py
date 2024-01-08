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
    'show_customer_data_v2',
    default_args=default_args,
    description='Download and show customers data',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:

    download_file = KubernetesPodOperator(
        task_id='download_customers_data',
        namespace='airflow',
        image="alpine:latest",
        cmds=["sh", "-c"],
        arguments=["./scripts/download_file.sh"],
        name="download-pod",
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod"
    )

    show_file = KubernetesPodOperator(
        task_id='show_customers_data',
        namespace='airflow',
        image="alpine:latest",
        cmds=["sh", "-c"],
        arguments=["./scripts/show_file.sh"],
        name="show-pod",
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod"
    )

    download_file >> show_file