from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_DIR = "/Users/laharivarma/Desktop/ecommerce-etl-pipeline"


default_args = {
    "owner": "lahari",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="olist_etl_pipeline",
    default_args=default_args,
    description="End-to-End ETL Pipeline for Olist E-Commerce Data",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    tags=["etl", "olist", "data-engineering"],
) as dag:

    extract = BashOperator(
        task_id="extract_data",
        bash_command=f"cd {PROJECT_DIR} && "
                     f"source .venv/bin/activate && "
                     f"python src/extract.py",
    )

    transform = BashOperator(
        task_id="transform_data",
        bash_command=f"cd {PROJECT_DIR} && "
                     f"source .venv/bin/activate && "
                     f"python src/transform.py",
    )

    validate = BashOperator(
        task_id="validate_data",
        bash_command=f"cd {PROJECT_DIR} && "
                     f"source .venv/bin/activate && "
                     f"python src/validate.py",
    )

    load = BashOperator(
        task_id="load_to_mysql",
        bash_command=f"cd {PROJECT_DIR} && "
                     f"source .venv/bin/activate && "
                     f"python src/load.py",
    )


    extract >> transform >> validate >> load