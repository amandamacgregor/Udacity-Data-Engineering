# Udacity Data Engineering Nanodegree - Complete Portfolio

Six projects that taught me how to translate technical decisions into business value. These projects taught me to think about: What problem does this solve? Why this tool over alternatives? How would I justify costs? What happens at scale?
The progression: Started with "make data queryable" → "make it fast" → "make it cheap at scale" → "make it reliable and automated" → "now design something end-to-end and defend every choice."
Important context: These are course projects using a fictional company (Sparkify). With this as the background, here are the technical skills I developed and the framework for thinking about business impact.

---

## The Journey: Skills Progression

```
Project 1: Data Modeling with Postgres
    ↓ (Learn relational modeling & ETL basics)
Project 2: Data Modeling with Cassandra  
    ↓ (Add NoSQL, query-first design)
Project 3: Cloud Data Warehouse with Redshift
    ↓ (Scale to cloud, infrastructure as code)
Project 4: Data Lake with Spark
    ↓ (Distributed computing, big data processing)
Project 5: Data Pipelines with Airflow
    ↓ (Automation, monitoring, production workflows)
Project 6: Capstone - Immigration & Temperature Analysis
    ↓ (Combine everything, demonstrate architectural thinking)
```

---

## Projects Overview

### 1. Data Modeling with Postgres - Star Schema ETL
**What I Built**: A PostgreSQL database with star schema optimized for song play analysis  
**Key Skills**: Relational modeling, normalization, SQL, Python ETL  
**Tech Stack**: PostgreSQL, Python, pandas, psycopg2

**The Scenario**: Simulated analytics team needed to query data scattered across JSON files. Without a proper database, every analysis requires custom scripts to join files first.

**What I Learned**:
- How to design star schemas (1 fact table, 4 dimension tables)
- The difference between OLTP (optimized for writes) vs OLAP (optimized for reads)
- Why denormalization makes sense in analytics despite violating 3NF
- How to write idempotent ETL scripts

**The Business Thinking**: The Business Thinking: This project taught me that technical decisions start with understanding how data will be used. If analysts need to slice by time/location/user demographics repeatedly, a star schema makes those queries fast and intuitive. The alternative - writing custom JOIN scripts for every analysis - wastes analyst time.

This taught me that good data modeling isn't just about technical correctness - it's about making analysts productive. A perfectly normalized 6NF database that requires 5-way JOINs for basic queries is worse than a slightly redundant star schema that just works.

**IRL, This Would Mean**: Before building any data infrastructure, I'd ask: "What are the top 10 questions users need to answer?" Then design the schema around those access patterns, not just around "proper" normalization..

This taught me that good data modeling isn't just about technical correctness - it's about making analysts productive. A perfectly normalized 6NF database that requires 5-way JOINs for basic queries is worse than a slightly redundant star schema that just works.

---

### 2. Data Modeling with Apache Cassandra - NoSQL Design
**What I Built**: A Cassandra database with three denormalized tables for specific queries  
**Key Skills**: NoSQL modeling, denormalization, partition keys, clustering columns  
**Tech Stack**: Apache Cassandra, Python, pandas

**The Scenario**: Simulated need for high-traffic, sub-millisecond lookups that Postgres couldn't handle at scale.

**What I Learned**:
- Query-first design: You define queries BEFORE creating tables
- Cassandra has no JOINs - everything needed must be in one table
- Data is duplicated across multiple tables optimized for different queries
- Partition keys determine data distribution and query performance

**The Trade-Off**: Cassandra is incredibly fast but inflexible. You get amazing read performance on known queries, but ad-hoc exploration is nearly impossible.

**The Business Thinking**: This project taught me there's no "best" database - only trade-offs. Cassandra makes sense when:
- You know your queries upfront
- You need consistent low latency at scale
- You can afford data duplication

It doesn't make sense when:
- Users need to explore data with unpredictable queries
- Data changes frequently (updates are expensive)
- Your team isn't comfortable with distributed systems

**IRL, This Would Mean**: If a product team asked for a new feature requiring database changes, I could evaluate: "Do we know the exact queries needed? Is this a read-heavy or write-heavy workload? What's our tolerance for eventual consistency?" Then recommend the right tool for the job.

Cassandra taught me that technology choices are business choices. Saying 'we should use X because it's industry standard' is lazy. The better answer is: 'Here's what we gain with X, here's what we lose, and here's why I think the trade-off makes sense for our use case.'

---

### 3. Cloud Data Warehouse with Amazon Redshift
**What I Built**: An ETL pipeline that moves data from S3 to Redshift via staging tables  
**Key Skills**: Cloud infrastructure, IaC, SQL optimization, MPP databases  
**Tech Stack**: AWS (S3, Redshift, IAM), Python, SQL, boto3

**The Scenario**: Simulated scale-up from single-machine Postgres to cloud-scale data warehouse.

**What I Learned**:
- Why S3 → Staging → Star Schema architecture (data validation, reproducibility, flexibility)
- Redshift's COPY command is 100x faster than INSERT for bulk loads
- Distribution keys (DISTKEY) and sort keys (SORTKEY) dramatically affect query performance
- Columnar storage only reads columns you actually query

**The Architecture Decision**:
```
S3 (raw data) → Staging Tables (validation) → Star Schema (optimized for queries)
```

**Why Staging Tables?** This was the key design decision I had to think through:
1. **Data validation**: Catch bad records before corrupting analytics tables
2. **Reproducibility**: Can rebuild star schema anytime without re-extracting from source
3. **Flexibility**: Business rules change; staging preserves all raw fields
4. **Performance**: Bulk COPY to staging is way faster than complex transformations during load

**The Cost-Benefit Thinking**: In a real scenario, I'd need to justify Redshift costs (~$500/month for a 4-node cluster). The case would be:
- **Current pain**: Postgres queries timing out, dashboards taking 10+ minutes
- **Proposed solution**: Redshift with proper optimization
- **Expected improvement**: Queries from minutes → seconds, supports 100+ concurrent users
- **ROI**: If analytics team saves 15 hours/week not waiting on queries, that's ~$30k/year in productivity
- **Break-even**: 5 months

**IRL, This Would Mean**: When evaluating cloud costs, I wouldn't just say "Redshift is expensive." I'd quantify the hidden cost of the current state (analyst time wasted, decisions delayed) and show the ROI.

This project taught me that technical optimization has business impact. 

---

### 4. Data Lake with Apache Spark - Big Data Processing
**What I Built**: EMR (elastic mapreduce)-based Spark job that processes JSON from S3 and writes parquet files back to S3  
**Key Skills**: Distributed computing, Spark DataFrames, parquet optimization, AWS EMR  
**Tech Stack**: Apache Spark (PySpark), AWS (S3, EMR), parquet, Python

**The Scenario**: Simulated need to process millions of records that don't fit in memory.

**What I Learned**:
- Spark's lazy evaluation optimizes the entire query plan before executing
- Wide transformations (groupBy, join) trigger expensive data shuffles
- Partitioning strategy dramatically affects performance
- Parquet format is both compressed and column-oriented

**The Data Lake vs Warehouse Question**: This project taught me when you need both:
- **Data Lake (S3 + Spark)**: Store everything raw and cheap; good for data science, ML, ad-hoc exploration
- **Data Warehouse (Redshift)**: Store cleaned, structured data; good for dashboards, business reports

Real-world scenario: Data scientists might want "all event data forever" for ML models. That's expensive to keep in Redshift. Solution: Keep 90 days in Redshift (fast queries), archive the rest to S3 (cheap storage), use Spark when historical analysis is needed.

**The Trade-Off**: Data lake is 95% cheaper for storage but slower for queries. Data warehouse is fast but expensive. Most companies need both.

**IRL, This Would Mean**: If data scientists asked for raw event history and Finance freaked out at storage costs, I could propose a hybrid: Recent data in warehouse, historical data in lake. Both sides get what they need.

**I've seen teams argue 'data lake vs warehouse' as if you must choose one. This project taught me they solve different problems. The skill is knowing which problem you're solving.

---

### 5. Data Pipelines with Apache Airflow - Production Orchestration
**What I Built**: Automated Airflow DAG that runs ETL from S3 → Redshift with monitoring and quality checks  
**Key Skills**: Workflow orchestration, custom operators, task dependencies, SRE practices  
**Tech Stack**: Apache Airflow, AWS (S3, Redshift), Python, SQL

**The Scenario**: All previous projects required manual execution. This automated everything with proper error handling, retries, and monitoring.

**What I Learned**:
- The difference between "script that works" and "production system"
- How to design DAGs with proper task dependencies
- Why data quality checks must fail loudly (not silently succeed with bad data)
- How to build idempotent pipelines (safe to rerun)

**Custom Operators I Built**:
1. **StageToRedshiftOperator** - S3 → Redshift COPY with JSON parsing
2. **LoadFactOperator** - Staging → fact table transformation
3. **LoadDimensionOperator** - Supports append or truncate-insert modes
4. **DataQualityOperator** - Runs SQL checks, fails pipeline if issues found

**The Airflow vs Cron Debate**: This project made me think about the real cost of "simple" solutions:

| What You Need | Cron Job | Airflow |
|---------------|----------|---------|
| Schedule tasks | ✅ Easy | ✅ Easy |
| Know when it failed | ❌ Check logs manually | ✅ Instant alerts |
| Retry failed tasks | ❌ Write custom logic | ✅ Built-in |
| Task dependencies | ❌ Hope timing works | ✅ Automatic |
| See execution history | ❌ Parse log files | ✅ Web UI |

**The Real Cost**: Cron is "free" but requires constant babysitting. In a real scenario, if data team spends 20 hours/week monitoring cron jobs, that's ~$50k/year in salary. Airflow takes 2 weeks to set up but then runs with minimal oversight.

**IRL, This Would Mean**: When someone proposes a manual process, I'd ask: "What's the ongoing maintenance cost?" Sometimes the "quick and dirty" solution is actually more expensive long-term.

**I've seen scripts break silently - nobody notices until users complain. This project taught me that production systems need monitoring, alerting, and automated recovery. That's not gold-plating; that's professionalism.

---

### 6. Capstone - Immigration & Temperature Data Lake
**What I Built**: Spark-based data lake combining 3M+ immigration records with global temperature data  
**Key Skills**: End-to-end data engineering, Spark optimization, data quality, scalability planning  
**Tech Stack**: Apache Spark, Python, pandas, parquet, Jupyter

**The Business Question**: Can we identify correlations between temperature patterns and immigration trends?

**What Made This Real**:
- Worked with actual messy data (invalid port codes, inconsistent formats)
- 3M+ records meant I had to think about memory management and partitioning
- Had to make architecture decisions and defend them in writing

**Key Challenges**:
1. **Data format**: Immigration data in proprietary .sas7bdat format
2. **Dirty data**: Invalid values like "XXX" that would break joins
3. **Fuzzy matching**: Linking city names to port codes with ~70% success rate
4. **Scale thinking**: Designed for 3M records locally, documented how to scale to 300M in production

**The Architectural Thinking**: 
For the capstone writeup, I had to answer: "What if data increased 100x?"

My response:
- **If frequency increased** (daily vs monthly): Add Airflow for scheduling, implement incremental loads
- **If volume increased** (300M records): Move to AWS EMR, use Redshift Spectrum for queries
- **If 100+ users needed access**: Build OLAP cube for common queries, implement row-level security

**What This Shows**: I can think beyond the current project to production realities. Yes, it runs on my laptop. But I documented exactly how it would scale when needed.

**IRL, This Would Mean**: When building something new, I'd design for current constraints but document the path to scale. No over-engineering, but also no dead-ends that require full rebuilds later.

**This capstone shows I can think architecturally. The code runs locally, but I designed it with cloud scale in mind - partitioning strategy, file formats, data model all translate to EMR/Redshift when ready. That's the difference between student code and production-ready design.

---

## Why This Portfolio Matters

### What These Projects Actually Taught Me:

**1. Technical Choices Are Business Choices**
Every "should we use X or Y" question has a business answer:
- Cost (upfront and ongoing)
- Time to implement
- Maintenance burden
- Scalability limits
- Team expertise required

**2. Explaining Complexity Simply**
Data engineers often struggle to explain why their work matters. These projects taught me to translate:
- "DISTKEY optimization" → "dashboards load 10x faster"
- "Staging tables" → "we catch bad data before it corrupts analytics"
- "Parquet format" → "95% cheaper storage for the same data"

**3. Production Thinking**
The difference between code that works and production systems:
- Works once vs works reliably
- Manual vs automated
- Silent failures vs loud failures
- "Hope it's right" vs "verified data quality"

### I Use This Daily:

- Product team proposes a feature → I evaluate data availability and technical feasibility
- Engineering suggests a solution → I ask about ongoing costs and maintenance burden  
- Leadership asks "why is this taking so long?" → I explain the difference between MVP and production-ready

---

## Key Technical Concepts I Can Discuss

- Star vs snowflake schemas, normalization trade-offs
- OLTP vs OLAP workloads
- Row-oriented vs columnar storage
- Partitioning strategies (range, hash, list)
- Query optimization and execution plans
- CAP theorem and eventual consistency
- Wide vs narrow transformations in Spark
- Batch vs streaming processing
- Data quality validation frameworks
- When to use Postgres vs Cassandra vs Redshift
- Spark vs pandas for data processing
- Airflow vs cron vs AWS Step Functions

---

## What's Next

These are course projects. Sparkify isn't real. I didn't actually negotiate with a CFO or convince a VP.

**But here's what IS real:**

✅ I built working data systems across 6 different technology stacks  
✅ I learned to think about trade-offs, not just "best practices"  
✅ I understand how to connect technical work to business outcomes  
✅ I can explain complex systems to non-technical people  
✅ I know the difference between code that works and production systems  

---

**Portfolio Stats**:
- 6 projects across 4 different tech stacks
- ~3,300 lines of code
- 3M+ records processed in capstone
- Countless hours learning to think like both an engineer and a PM
