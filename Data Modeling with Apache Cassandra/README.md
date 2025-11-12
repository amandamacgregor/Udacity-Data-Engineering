# Project 2: Data Modeling with Apache Cassandra

## What I Built
A NoSQL database with three denormalized tables, each optimized for a specific query pattern. This project taught me query-first design - you define your questions before building your schema.

## Tech Stack
- **Apache Cassandra** - Distributed NoSQL database
- **Python** - ETL pipeline and data processing
- **pandas** - Data manipulation and CSV processing
- **cassandra-driver** - Python driver for Cassandra

## The Business Problem (Learning Scenario)
Sparkify's analytics team needed to query song play data with sub-millisecond response times at scale. Their questions were specific and known upfront:
1. What song was playing in a specific session?
2. What songs did a user play in a particular session?
3. Who listened to a specific song?

With Postgres, as traffic grew, these queries would slow down. They needed a database optimized for these exact access patterns, even if it meant sacrificing flexibility.

## The Cassandra Mindset Shift

### From SQL Thinking:
1. Normalize data into logical entities
2. Design schema around data relationships
3. Use JOINs to answer any question
4. One schema serves all queries

### To Cassandra Thinking:
1. Start with the queries you need to answer
2. Design one table per query
3. Denormalize everything - no JOINs allowed
4. Duplicate data across multiple tables

**This was the hardest mental shift in the entire nanodegree.**

## The Three Tables (Query-First Design)

### Table 1: Session Library
**Query**: "Give me the artist, song title and song length that was heard during sessionId = 338, and itemInSession = 4"

```sql
CREATE TABLE session_library (
    session_id int,
    item_in_session int,
    artist_name text,
    song_title text,
    song_length float,
    PRIMARY KEY (session_id, item_in_session)
)
```

**Key Design Decisions**:
- **Partition key**: `session_id` - All data for a session lives on the same node
- **Clustering column**: `item_in_session` - Orders songs within the session
- **Why this works**: Cassandra can find the partition instantly, then scan to the specific item

### Table 2: User Session Library
**Query**: "Give me the artist name, song (sorted by itemInSession) and user (first and last name) for userId = 10, sessionId = 182"

```sql
CREATE TABLE user_session_library (
    user_id int,
    session_id int,
    item_in_session int,
    artist_name text,
    song_title text,
    first_name text,
    last_name text,
    PRIMARY KEY ((user_id, session_id), item_in_session)
) WITH CLUSTERING ORDER BY (item_in_session ASC)
```

**Key Design Decisions**:
- **Composite partition key**: `(user_id, session_id)` - Need both to find the data
- **Clustering column**: `item_in_session` - Maintains sort order
- **Why composite partition**: Neither user_id nor session_id alone is unique enough

### Table 3: Song User Library
**Query**: "Give me every user name (first and last) who listened to the song 'All Hands Against His Own'"

```sql
CREATE TABLE song_user_library (
    song_title text,
    user_id int,
    first_name text,
    last_name text,
    PRIMARY KEY (song_title, user_id)
)
```

**Key Design Decisions**:
- **Partition key**: `song_title` - All listeners of a song together
- **Clustering column**: `user_id` - Ensures uniqueness (users can listen multiple times)
- **Why this works**: Single partition holds all listeners for a song

## The ETL Pipeline

### Step 1: Data Consolidation
Original data scattered across daily CSV files:
```
event_data/2018-11-01-events.csv
event_data/2018-11-02-events.csv
...
event_data/2018-11-30-events.csv
```

**ETL Process**:
1. Iterate through all CSV files in directory
2. Combine into single `event_datafile_new.csv`
3. Filter out records where `artist` is NULL (incomplete sessions)

### Step 2: Table Creation
- Connect to local Cassandra cluster
- Create keyspace `sparkifydb`
- Drop tables if they exist (idempotent)
- Create three tables with appropriate primary keys

### Step 3: Data Loading
For each table:
1. Read from consolidated CSV
2. Extract only the columns needed for that table
3. INSERT with prepared statements
4. Verify with SELECT query

### Step 4: Validation
Run the three queries to verify data loaded correctly and returns expected results.

## Technical Challenges

### Challenge 1: Understanding Primary Keys
In Cassandra, PRIMARY KEY has two parts:
- **Partition key**: Determines which node stores the data
- **Clustering columns**: Determines sort order within the partition

Getting this wrong means:
- Hot partitions (all data on one node)
- Slow queries (scanning instead of seeking)
- Duplicate data (non-unique primary key)

### Challenge 2: Data Duplication
Same user/song data appears in all three tables. In SQL this violates normalization. In Cassandra, it's required.

**Why it's okay**:
- Storage is cheap
- Network shuffling (JOINs) is expensive
- Read performance matters more than storage efficiency

### Challenge 3: Query Limitations
You can ONLY query by:
- Full partition key
- Full partition key + clustering columns
- Full partition key + range on clustering columns

**This won't work**: `SELECT * FROM session_library WHERE artist_name = 'Coldplay'`  
**Why**: `artist_name` isn't part of the PRIMARY KEY

To support that query, you'd need a fourth table with `artist_name` as partition key.

## What I Learned

### 1. No Silver Bullet Databases
Cassandra excels at:
- ✅ Known queries with high traffic
- ✅ Write-heavy workloads
- ✅ Need for linear scalability
- ✅ Multi-datacenter replication

Cassandra struggles with:
- ❌ Ad-hoc queries (can't query non-key columns)
- ❌ Complex aggregations (no GROUP BY, no JOINs)
- ❌ Frequent schema changes (denormalization makes changes expensive)
- ❌ Small datasets (overhead isn't worth it)

### 2. The Query-First Discipline
Before Cassandra, I'd design schemas and figure out queries later. Cassandra forces you to:
1. List every query you'll need
2. Design a table for each query
3. Accept that new queries might require new tables

**This is actually a great discipline for product work.** Forces you to think about requirements upfront.

### 3. Trade-Offs Are Real
The "best practice" in SQL (normalize everything) is an anti-pattern in Cassandra. The "bad practice" in SQL (denormalize, duplicate data) is required in Cassandra.

**The lesson**: Stop asking "what's the best way" and start asking "what's the best way for THIS use case?"

## How I'd Apply This at IRL

### Scenario: High-Traffic Lookups
If we had a feature requiring sub-millisecond lookups with known queries (e.g., "get user preferences by userId"), I'd evaluate:

**Postgres**:
- ✅ Easy to query flexibly
- ❌ Vertical scaling limits
- ❌ Slower at high concurrency

**Cassandra**:
- ✅ Linear scalability
- ✅ Consistent low latency
- ❌ Requires knowing queries upfront
- ❌ Team learning curve

**Recommendation**: Start with Postgres (easier), migrate to Cassandra when we hit scale limits AND our queries are stable.

### The Conversation I'd Have
**Product**: "We need to store user preferences"  
**Me**: "What queries will we run?"  
**Product**: "Get preferences by userId, update preferences"  
**Me**: "Any other queries? Will we need to filter by preference type? Search across users?"  
**Product**: "Not initially"  
**Me**: "Then Postgres is fine to start. If we hit performance issues at scale AND our queries stay simple, we can migrate to Cassandra later."


## Talking Points

**My Cassandra project forced me to unlearn SQL** 
In Postgres, you normalize data and use JOINs. In Cassandra, you denormalize everything and duplicate data across tables. 

At first I thought it was wrong - violating every database principle I'd learned. But then I realized: those principles optimize for flexibility. Cassandra optimizes for speed on known queries. Neither is 'right' - they're optimizing for different goals.

'What is this optimized for? Does that match what we need?' Stops me from suggesting 'best practices' that might not fit our use case.


**Start with the access patterns**
- Lots of JOINs and ad-hoc queries? → SQL (Postgres, MySQL)
- Known queries, need consistent low latency? → Cassandra
- Need ACID transactions? → SQL
- Need multi-datacenter replication? → Cassandra
- Small team without distributed systems experience? → SQL

My Cassandra project taught me that 'NoSQL' isn't better than SQL - it's just different. The skill is matching the tool to the requirement, not picking what's trendy."

Picking Cassandra because it's 'web scale' when they have 10,000 users and unknown query patterns. I learned this from my project: Cassandra requires discipline. You have to know your queries upfront and accept data duplication.

If you're still figuring out what questions you need to answer, start with Postgres. Add Cassandra when you have proven scale problems AND stable queries.

## Project Structure

```
Project_1B_Project_Template.ipynb  # Main notebook with ETL pipeline
event_data/                         # Directory of daily CSV files
  2018-11-01-events.csv
  2018-11-02-events.csv
  ...
event_datafile_new.csv             # Consolidated data file (generated by ETL)
images/                            # Screenshots of data and results
README.md                          # This file
```

## Key Metrics
- **Files processed**: 30 daily CSV files
- **Records consolidated**: 6,820 events
- **Tables created**: 3 denormalized tables
- **Queries optimized**: 3 specific access patterns
- **Query performance**: Sub-millisecond lookups

## What's Missing (Honestly)

This is a learning project, so it doesn't include:
- Replication strategy (production Cassandra uses RF=3)
- Consistency levels (ONE, QUORUM, ALL)
- Production cluster setup (this uses local single-node)
- Monitoring and performance tuning
- Security and access control
- Backup and disaster recovery

**But the mental model is solid** - query-first design, partition key selection, accepting denormalization. Those translate to production work.

## Skills Demonstrated
- NoSQL data modeling (query-first design)
- Understanding partition keys and clustering columns
- Denormalization and data duplication strategies
- ETL pipeline development
- Python + Cassandra integration
- Trade-off analysis (Cassandra vs SQL)

---

**Bottom Line**: This project taught me that good data modeling starts with understanding how data will be accessed, not just how it should be structured. That's a lesson that applies to every database technology - and honestly, to product design in general. Requirements should drive design, not the other way around.
