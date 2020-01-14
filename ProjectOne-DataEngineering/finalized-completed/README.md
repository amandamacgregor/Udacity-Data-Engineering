Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals:

## Purpose
The purpose of this database is to allow a Startup, Sparkify, to reach their analytical goals. A primary analytical goal for the company is to understand what songs users are listening to. The state of their data before building out this relational database consisted of two local directories of JSON data. 

This project built out a relational database schema and ETL pipeline to provide insights from that JSON data.


## Database Schema Design
The Relational Database design for this project consisted of a Star Schema, with one Fact table and four Dimension tables:
* Fact Table: Table Name = songplays (records in log data associated with song plays) Table Columns = start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
* Dimension Table: Table Name = users (users in the app) Table Columns = user_id, first_name, last_name, gender, level
* Dimension Table: Table Name = songs (songs in music database) Table Columns = song_id, title, artist_id, year, duration
* Dimension Table: Table Name = artists (artists in music database) Table Columns = artist_id, name, location, latitude, longitude
* Dimension Table: Table Name = time (timestamps of records in songplays broken down into specific units) Table Columns = start_time, hour, day, week, month, year, weekday

This allows for normalized data (for example, each cell contains unique and and single values), flexible queries (for example, common SQL ability), one table per entity (for example, user data is store on a table seperate from artist data, etc).

One fact table (songplays) consists of the measurements of Sparkify's processes around music streaming and users are listening to. The remaining tables act as structures that categorize those measurements.


In total, this project contains:
* Data folder with the JSON data the feeds into the ETL pipeline
* create_tables.py file for creating the database and tables
* etl.ipynb for a user-friendly Jupyter walkthrough of the ETL process
* etl.py, which is the ETL pipeline
* sql_queries.py contains the drop, create, insert, find and query scripts
* Finally, test.ipynb is a Jupyter notebook to view data that's been inserted via the ETL pipeline to confirm success and take a look at the first few columns of each of the five tables.


## How to Use
1. Once in the project, click on the + sign in the menu near the top left of the screen and select Terminal, under Other.
2. In the command-line, type: python create_tables.py
3. In the command-line, type: python etl.py
4. Once these commands run (without errors), open test.ipynb and run each block of code in sequence to review the data the ETL pipeline successfully extracted, transformed and loaded from the JSON datasets into the new relational database, as outlined above.

NOTE: You will not be able to run test.ipynb, etl.ipynb, or etl.py until you have run create_tables.py at least once to create the sparkifydb database, which these other files connect to.

