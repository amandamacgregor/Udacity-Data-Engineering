from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table_names=[""],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
            self.redshift_conn_id = redshift_conn_id
            self.table_names = table_names

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        for table in self.table_names:
            row = redshift.get_records(f"SELECT COUNT(*) FROM {table}")
            if len(records) < 1 or len(row[0]) < 1:
                raise ValueError(f"Data check failed. {table} returned no results")

        data_checks=[
            {'table': 'artists',
             'check_sql': "SELECT COUNT(*) FROM users WHERE artistid is null",
             'expected_result': 0},
            {'table': 'songs',
             'check_sql': "SELECT COUNT(*) FROM songs WHERE songid is null",
             'expected_result': 0}
        ]
        for check in data_check:
             row = redshift.get_records(check['check_sql'])
             if row[0] != check['expected_result']:
                raise ValueError(f"Data check failed. {check['table']} \
                                   contains null in id column")