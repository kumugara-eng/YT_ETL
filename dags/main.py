from airflow import DAG
import pendulum
from datetime import timedelta ,datetime
from api.video_stats import get_playlist_id, get_video_ids, extract_video_details, save_to_json
from datawarehouse.dwh import ( staging_table, core_table )
from dataquality.soda import yt_elt_data_quality
from airflow.operators.trigger_dagrun import TriggerDagRunOperator





local_tz = pendulum.timezone("Africa/Gaborone")


'''
The start_date is the time when the DAG will start running. 
It is set to January 1, 2023, in the Africa/Gaborone timezone.

but the DAG will not run until the start_date is reached.

'''
default_args = {
    'owner': 'dataengineers',
    'depends_on_past': False,
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    "email": ["dataengineers@example.com"],
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    "max_active_runs" : 1,
    "dagrun_timeout":timedelta(minutes=60),
    #"end_date": datetime(2027, 12, 31,tzinfo=local_tz),
 
}

with DAG(
    dag_id='produce_json_file',
    default_args=default_args,
    description='Dag to extract raw data and save to json file',
    schedule_interval='0 14 * * *',  # Run daily at 14:00 (2 PM)
    catchup=False,  # dont catch up on past runs
) as dag_produce:
    

    # define the tasks
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_details = extract_video_details(video_ids)
    save_tojson = save_to_json(video_details)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )

    #set task dependencies
    playlist_id >> video_ids >> video_details >> save_tojson >> trigger_update_db

with DAG(
    dag_id='update_db',
    default_args=default_args,
    description='Dag to update staging and core tables in the data warehouse with the latest data from the JSON file',
    catchup=False,  # dont catch up on past runs
    schedule=None
) as dag_update:
    

    # define the tasks
    update_staging = staging_table()
    update_core = core_table()
  
    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality_checks",
    )

    #set task dependencies
    update_staging >> update_core >> trigger_data_quality



with DAG(
    dag_id='data_quality_checks',
    default_args=default_args,
    description='Dag to perform data quality checks on the staging and core tables in the data warehouse',
    catchup=False,  # dont catch up on past runs
    schedule=None
) as dag_quality:
    

    # define the tasks
    data_quality_staging = yt_elt_data_quality(schema="staging")
    data_quality_core = yt_elt_data_quality(schema="core")

  


    #set task dependencies
    data_quality_staging >> data_quality_core
    
    




