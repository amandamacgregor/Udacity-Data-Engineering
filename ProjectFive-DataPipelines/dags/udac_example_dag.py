from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator, PostgresOperator)
from helpers import SqlQueries
# from helpers import CreateTables

AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')

#     use python callables to log twice in process
def start_dag():
    logging.info("DAG is kicking off!")
    
def end_dag():
    logging.info("DAG complete!")

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
#     'end_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@hourly'
        )

start_operator = DummyOperator(
    task_id='Begin_execution',
#     use python callable to log
    python_callable=start_dag, 
    dag=dag
)

# create_table = PostgresOperator(
#     task_id="create_tables",
#     postgres_conn_id="redshift",
#     sql=SqlQueries.create_tables,
#     dag=dag
# )

stage_events_to_redshift = StageToRedshiftOperator(
    task_id= 'Stage_events',
    provide_context=True,
    table = "public.staging_events",
    s3_path = 's3://udacity-dend/log_data',
    redshift_conn_id= 'redshift',
    aws_conn_id= 'aws_credentials',
    region= 'us-west-1',
    data_format= 'JSON',
    dag=dag
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id= 'Stage_songs',
    provide_context=True,
    table = "public.staging_songs",
    s3_path = 's3://udacity-dend/song_data',
    redshift_conn_id= 'redshift',
    aws_conn_id= 'aws_credentials',
    region= 'us-west-1',
    data_format= 'JSON',
    dag=dag
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    redshift_conn_id='redshift',
    table="public.songplays",
    select_sql=SqlQueries.songplay_table_insert,
    append_only=True,
    dag=dag
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    redshift_conn_id='redshift',
    table="public.users",
    select_sql=SqlQueries.user_table_insert,
    mode='truncate',
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    redshift_conn_id='redshift',
    table="public.songs",
    select_sql=SqlQueries.song_table_insert,
    mode='truncate',
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    redshift_conn_id='redshift',
    table="public.artists",
    select_sql=SqlQueries.artist_table_insert,
    mode='truncate',
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    redshift_conn_id='redshift',
    table="public.time",
    select_sql=SqlQueries.time_table_insert,
    mode='truncate',
    dag=dag
)

# For example one test could be a SQL statement that checks if certain column contains NULL values by counting all the rows that have NULL in the column. We do not want to have any NULLs so expected result would be 0 and the test would compare the SQL statement's outcome to the expected result.
run_quality_checks = DataQualityOperator(
        task_id='run_data_quality_checks',
        redshift_conn_id="redshift",
        table_names=["public.staging_events", "public.staging_songs",
                    "public.songplays", "public.artists",
                    "public.songs", "public.time", "public.users"]
)

end_operator = DummyOperator(
    task_id='Stop_execution',
#     use python callable to log
    python_callable=end_dag, 
    dag=dag
)

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift
# create_tables >> stage_events_to_redshift
# create_tables >> stage_songs_to_redshift
stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table
load_songplays_table >> load_user_dimension_table >> run_quality_checks
load_songplays_table >> load_song_dimension_table >> run_quality_checks
load_songplays_table >> load_artist_dimension_table >> run_quality_checks
load_songplays_table >> load_time_dimension_table >> run_quality_checks
run_quality_checks >> end_operator