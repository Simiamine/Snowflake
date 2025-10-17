from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/airflow/repo/course/airbnb"
DBT_PROFILES_DIR = "/opt/airflow/repo/course/airbnb"
DBT_TARGET = "dev"

default_args = {"owner": "airflow", "depends_on_past": False, "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="airbnb_dbt_daily",
    description="dbt pipeline for Airbnb project on Snowflake",
    default_args=default_args,
    start_date=datetime(2025, 10, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["dbt", "airbnb", "snowflake"],
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"set -euo pipefail; dbt deps --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"set -euo pipefail; dbt seed --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET} --full-refresh",
    )

    dbt_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"set -euo pipefail; dbt source freshness --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET} --output json > /opt/airflow/logs/dbt_freshness.json || true",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"set -euo pipefail; dbt build --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_test_playground = BashOperator(
        task_id="dbt_test_playground",
        bash_command=(
            f"set -euo pipefail; "
            f"dbt test --select avg_price_by_room_type "
            f"--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"set -euo pipefail; dbt docs generate --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_deps >> dbt_seed >> dbt_freshness >> dbt_build >> dbt_test_playground >> dbt_docs
