from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client.models import V1Volume, V1VolumeMount

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
        arguments=[
            'file_url="https://ifood-data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz"',
            'curl -sSL "$file_url" | gzip -d > /mnt/files/customers.csv && echo "File downloaded successfully!" || echo "Error downloading file!"'
        ],
        name="download-pod",
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod",
        volumes=[
            V1Volume(name="airflow-files", persistent_volume_claim={"claimName": "airflow-files"}),
        ],
        volume_mounts=[
            V1VolumeMount(name="airflow-files", mount_path="/mnt/files"),
        ],
    )

    show_file = KubernetesPodOperator(
        task_id='show_customers_data',
        namespace='airflow',
        image="alpine:latest",
        cmds=["sh", "-c"],
        arguments=["cat /mnt/files/customers.csv"],
        name="show-pod",
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod"
    )

    download_file >> show_file
