# Project 6: Data Engineering Capstone - Immigration & Temperature Analysis

## What I Built
A data lake solution that combines U.S. immigration data with global temperature data, allowing analysts to explore correlations between climate patterns and immigration trends. Built using Spark for ETL, designed to scale to production with proper data modeling and quality checks.

## The "Why" Behind This Project
This was an open-ended capstone where we could demonstrate everything learned in the nanodegree. I chose to work with:
- **I94 Immigration Data** (US National Tourism and Trade Office) - 3M+ records
- **World Temperature Data** (Kaggle) - Global city temperatures over time

**The business question**: Can we identify patterns between temperature changes in origin cities and immigration patterns to the U.S.? This kind of analysis could inform policy decisions, resource allocation, or even tourism forecasting.

## Tech Stack & Constraints
- **Apache Spark** - For distributed data processing
- **Python** - ETL logic and data cleaning
- **Jupyter Notebook** - Development environment
- **Parquet files** - Storage format (optimized for analytics)
- **SQL** - Data transformations via Spark SQL

**Important context**: At the time of this project, I didn't have AWS access at work, so I deliberately limited the tech stack to what I could run locally and prototype. The design still accounts for how this would scale in production (see "Scaling Scenarios" below).

## Architecture: Star Schema

### Fact Table: `immigration_temperature_facts`
The analytical core - each row is an immigration event with associated temperature data:
- `arrival_date` - When someone arrived in U.S.
- `departure_date` - When they left
- `temperature` - Average temp in destination city
- `city` - Origin city code (i94cit)
- `temp_city` - Actual city name from temperature dataset
- `month` - Month of travel
- `travel_code` - Mode of transportation
- `i94port` - U.S. destination port/city
- `reason` - Visa category
- `year` - Year of event

### Dimension Table 1: `immigration`
Details about each immigration record:
- Arrival/departure dates
- Origin and destination codes
- Travel mode, visa type
- Partitioned by `i94port` for query optimization

### Dimension Table 2: `temperature`
Global temperature metrics by city:
- Average temperature
- City, Country, Lat/Long
- Linked via `i94portcode`
- Also partitioned by `i94portcode`

## The ETL Process

### Step 1: Data Exploration & Assessment
**Problem discovered**: Immigration data had invalid port codes like "XXX" and NaN values that would break joins.

**Solution**: Created a validation dictionary (`i94port.txt`) from official sources, filtered out invalid entries before processing.

### Step 2: Data Cleaning
```python
# Filter immigration data to valid ports only
df_imm = df_imm.filter(df_imm.i94port.isin(list(i94port.keys())))

# Remove temperature records with null values and duplicates
temp = temp.filter(temp.AverageTemperature != 'NaN')
temp = temp.dropDuplicates(['City', 'Country'])
```

### Step 3: Enrichment Challenge
Had to map city names in the temperature dataset back to i94port codes. Created a UDF (User Defined Function) to fuzzy match:
```python
@udf()
def addin_i94(city_name):
    for key in i94port:
        if city_name.lower() in i94port[key][0].lower():
            return key
```

This wasn't perfect (fuzzy matching never is), but it linked ~70% of temperature records to immigration ports.

### Step 4: Transformation & Loading
Used Spark SQL to join datasets and create the fact table:
```sql
SELECT 
    imm.arrdate as arrival_date,
    imm.depdate as departure_date,
    temp.AverageTemperature as temperature,
    imm.i94cit as city,
    temp.City as temp_city,
    imm.i94mon as month,
    imm.i94mode as travel_code,
    imm.i94port as i94port,
    imm.i94visa as reason,
    INT(imm.i94yr) as year
FROM immigration_view imm
JOIN temperature_view temp 
    ON (imm.i94port = temp.i94portcode)
```

**Key insight**: Had to use Spark temporary views instead of direct table joins due to some Spark SQL quirks in the notebook environment.

### Step 5: Partitioning Strategy
All tables partitioned by `i94port` because:
- Most queries will filter by destination city
- Enables parallel processing in production
- Reduces scan time for regional analysis (e.g., "all NYC arrivals")

## Data Quality Checks
Implemented row count validation at each stage:

```python
def quality_check_imm(df, description):
    result = df.count()
    imm_count = immigration.count()
    if result == imm_count:
        print(f"Data check passed for {description}: {result} rows")
    else:
        print(f"Data check failed for {description}")
```

**Results**:
- Immigration table: 3,088,544 rows ✓
- Temperature table: 3,490 rows ✓
- Fact table: Successfully joined subset ✓

## Technical Challenges

### Challenge 1: SAS File Format
Immigration data was in `.sas7bdat` format (not exactly beginner-friendly). Had to:
- Add Spark package: `saurfang:spark-sas7bdat:2.0.0-s_2.11`
- Use pandas for initial exploration, Spark for processing

### Challenge 2: Data Volume
3M+ immigration records meant:
- Had to think about memory management
- Used `.mode("append")` instead of loading everything at once
- Partitioning became critical, not just a "nice to have"

### Challenge 3: City Name Mapping
Temperature dataset used city names ("New York"), immigration used codes ("NYC"). The fuzzy matching UDF was imperfect:
- Missed some valid cities (false negatives)
- Occasionally matched wrong cities (false positives)

**Production solution**: Would build a proper lookup table with manual verification for top 100 cities, then use the UDF only for tail cases.

## Scaling Scenarios (From Project Write-Up)

### "What if data increased 100x?"
**If frequency increased** (daily instead of monthly):
- Implement **Apache Airflow** for scheduling and monitoring
- Set up DAGs with proper error handling and alerts
- Add incremental loading (only process new data)

**If volume increased** (300M records):
- Move to **AWS EMR** (managed Spark clusters)
- Use **Redshift Spectrum** for direct querying of S3 parquet files
- Implement dynamic partitioning by date AND port
- Consider columnar storage optimizations

### "What if pipeline needs to run daily by 7am?"
- **Airflow with SLAs** to guarantee completion time
- Build in monitoring/alerting if upstream data is late
- Add automated data validation before making data available
- Implement rollback capability if bad data gets loaded

### "What if 100+ users need access?"
- Build **OLAP cube** for common queries (pre-aggregated metrics)
- Implement **row-level security** if needed (some immigration data is sensitive)
- Use **Redshift** for fast analytical queries (star schema is perfect for this)
- Create **materialized views** for frequently-run reports
- Add **query result caching** to reduce repeated computation

## Talking Points

**Spark because..**
- Native support for SAS file format via community packages
- Can process 3M+ rows without running out of memory
- Parquet output format is analytics-optimized
- Easy to scale to EMR when ready

**Biggest lesson**
Sometimes the "right" tool depends on constraints. I could have done this entirely in AWS (S3, Glue, Athena), but proving I could build a functional pipeline with limited resources showed problem-solving skills. In a real job, you don't always have the perfect tech stack - you work with what you've got.

**Improve the city matching logic**
1. Create a reference table with official i94port ↔ city name mappings
2. Use fuzzy matching libraries like `fuzzywuzzy` for remaining matches
3. Add confidence scoring - flag low-confidence matches for manual review
4. Build an admin interface for data stewards to validate new city matches
5. Track match failures to identify patterns (missing data vs. bad data)

**Data refresh strategy**
Immigration data: **Monthly updates** align with government reporting cycles
Temperature data: **Quarterly updates** are sufficient for climate trend analysis
Fact table: **Rebuild monthly** after new immigration data loads

## Real-World Application
If I were building this IRL:
1. Add **data lineage tracking** - critical for government compliance
2. Implement **PII redaction** for sensitive immigration fields
3. Build **audit logs** for who accessed what data and when
4. Create **role-based views** (analysts see aggregates, investigators see details)
5. Add **data retention policies** (immigration data has specific retention requirements)

## Skills Demonstrated
- Distributed computing with Apache Spark
- Large-scale ETL design (3M+ records)
- Data modeling (star schema for analytics)
- Data quality validation and testing
- Partitioning strategies for performance
- Handling multiple data formats (SAS, CSV, Parquet)
- Scalability planning and architecture decisions
- Working within constraints (no cloud access)

## Project Files
- `capstone.ipynb` - Full ETL pipeline with exploration
- `i94port.txt` - Port code validation dictionary
- `schema.png` - Visual data model
- `/results/*.parquet` - Output dimension and fact tables

---

**Bottom Line**: This capstone demonstrates end-to-end data engineering - from messy source data to a clean, queryable data model. The focus on "how would this scale?" shows I'm thinking beyond the current project to production realities. It's one thing to process 3M rows on your laptop; it's another to design for 300M rows in production with SLAs, security, and monitoring.
