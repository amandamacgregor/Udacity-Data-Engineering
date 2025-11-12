# Project 5: Data Pipelines with Apache Airflow

## What I Built
An automated ETL pipeline using Apache Airflow that loads JSON data from S3 into Redshift, transforms it into a star schema, and runs data quality checks. Think of it as taking everything we learned in the Redshift project and putting it on autopilot with proper monitoring and error handling.

## Tech Stack
- **Apache Airflow** - Workflow orchestration (DAGs, operators, task dependencies)
- **AWS S3** - Source data storage (log_data and song_data JSON files)
- **AWS Redshift** - Data warehouse destination
- **Python** - Custom operators and SQL helpers
- **PostgreSQL** - Underlying Redshift connection

## The Pipeline Flow
1. **Stage to Redshift**: Copy JSON data from S3 to staging tables using Redshift's COPY command
2. **Load Fact Table**: Transform staged data into the `songplays` fact table
3. **Load Dimension Tables**: Populate `users`, `songs`, `artists`, and `time` dimension tables
4. **Data Quality Checks**: Verify all tables have data and meet quality standards

## What Made This Different
This was the first project where I wasn't manually running scripts - everything needed to be:
- **Automated** - Scheduled to run on its own
- **Monitored** - Built-in logging and alerts
- **Idempotent** - Can run multiple times without breaking things
- **Resilient** - Automatic retries on failure

## Key Learning: Custom Operators
Built four custom Airflow operators from scratch:
- `StageToRedshiftOperator` - Handles S3 → Redshift COPY with JSON path specs
- `LoadFactOperator` - Inserts into fact table from staging
- `LoadDimensionOperator` - Supports both append and truncate-insert modes
- `DataQualityOperator` - Runs configurable SQL checks (row counts, null checks, etc.)

## Technical Challenges

### Challenge 1: JSON Path Specifications
The log data had nested JSON that Redshift's COPY command couldn't parse automatically. Had to create a JSONPaths file to map the structure:
```json
{
    "jsonpaths": [
        "$['artist']",
        "$['auth']",
        "$['firstName']",
        // ... etc
    ]
}
```

### Challenge 2: Task Dependencies & Parallelization
Had to think through which tasks could run in parallel vs. which needed to wait:
- Staging tasks → Run in parallel (independent data sources)
- Dimension loads → Run in parallel after staging completes
- Fact table → Wait for all dimensions (FK constraints)
- Quality checks → Wait for everything

Set it up using Airflow's `>>` and `set_downstream()` operators.

### Challenge 3: Idempotency
Dimension tables needed to support two modes:
- **Append mode** - Add new records (for slowly changing dimensions)
- **Truncate-insert mode** - Full refresh each run (what we used)

Had to build this flexibility into the operator with a `mode` parameter.

## DAG Configuration
```python
default_args = {
    'owner': 'amanda',
    'depends_on_past': False,
    'start_date': datetime(2018, 11, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}
```

No `catchup` because we don't need to backfill historical runs - just process current data going forward.

## Data Quality Checks
Implemented multiple validation layers:
1. **Row count checks** - Ensure tables aren't empty
2. **NULL checks** - Verify critical columns have no NULL values
3. **Referential integrity** - FK validation between fact and dimension tables

If any check fails → pipeline stops, sends alert, allows for investigation.

## Talking Points

**"Why Airflow over cron jobs or Lambda?"**
- Visual DAG representation - can see dependencies and execution history
- Built-in retry logic and error handling
- Centralized logging and monitoring
- Community operators for common tasks (S3, Redshift, etc.)
- Can scale horizontally with Celery/Kubernetes executors

**"How would you optimize this pipeline?"**
- Add SLAs and alerting for missed deadlines
- Implement incremental loads instead of full refreshes (date-based partitioning)
- Use Airflow Variables/Connections for better secret management
- Add backfill capability for historical data recovery
- Consider using XComs to pass data between tasks if needed

**"What about data quality beyond basic checks?"**
- Could add schema validation (expected columns, data types)
- Business logic checks (e.g., "user_id should always be numeric")
- Anomaly detection (e.g., "row counts shouldn't vary >10% day-over-day")
- Data freshness checks (max timestamp in source data)

## Real-World Lessons
- **Start simple, add complexity** - Built basic operators first, added features iteratively
- **Logging is your friend** - Every operator action gets logged for debugging
- **Test locally first** - Airflow's webserver lets you manually trigger tasks for testing
- **Monitor resource usage** - Staging large datasets can exhaust Redshift cluster resources

## What I'd Do Differently
If I were building this IRL:
1. Use Airflow on AWS MWAA (Managed Workflows for Apache Airflow) instead of self-hosted
2. Implement more granular data quality checks tied to business KPIs
3. Add data lineage tracking (where did this data come from?)
4. Build a notification system (Slack/email) for pipeline failures
5. Use Airflow's SensorOperators to wait for S3 file availability before starting

## Skills Demonstrated
- Workflow orchestration and DAG design
- Custom Python operator development
- AWS service integration (S3, Redshift, IAM)
- ETL automation and scheduling
- Data quality validation frameworks
- Production-ready error handling and retry logic

---

**Bottom Line**: This project simulated a real production data pipeline where reliability, automation, and monitoring are just as important as getting the transformations right. It's the bridge between "I can write ETL scripts" and "I can build production data infrastructure."
