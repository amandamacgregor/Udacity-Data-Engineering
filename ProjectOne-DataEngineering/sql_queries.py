# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

songplay_table_create = ("""
        CREATE TABLE IF NOT EXISTS \
        songplays (
        songplay_id varchar NOT NULL,
        user_id varchar NOT NULL,
        level varchar NOT NULL,
        song_id varchar,
        artist_id varchar,
        session_id int NOT NULL,
        location varchar,
        user_agent varchar);
        """)

user_table_create = ("""
        CREATE TABLE IF NOT EXISTS 
        users (
        user_id varchar NOT NULL,
        first_name varchar,
        last_name varchar,
        gender char,
        level varchar);
        """)

song_table_create = ("""
        CREATE TABLE IF NOT EXISTS 
        songs (
        song_id varchar,
        title varchar NOT NULL,
        artist_id varchar,
        year int NOT NULL,
        duration float NOT NULL
        );
        """)

artist_table_create = ("""
        CREATE TABLE IF NOT EXISTS 
        artists (
        artist_id varchar,
        name varchar NOT NULL,
        location varchar NOT NULL,
        latitude float,
        longitude float);
        """)

time_table_create = ("""
        CREATE TABLE IF NOT EXISTS 
        time (
        start_time timestamp NOT NULL,
        hour int NOT NULL,
        day int NOT NULL,
        week int NOT NULL,
        month int NOT NULL,
        year int NOT NULL,
        weekday int NOT NULL);
        """)

# INSERT RECORDS

songplay_table_insert = ("""INSERT INTO 
                        songplays(songplay_id, user_id, level, song_id, artist_id, session_id, location, user_agent) 
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s);""")

user_table_insert = ("""INSERT INTO 
                    users(user_id, first_name, last_name, gender, level)
                    VALUES(%s,%s,%s,%s,%s);""")

song_table_insert = ("""INSERT INTO 
                    songs(song_id, title, artist_id, year, duration)
                    VALUES(%s,%s,%s,%s,%s);""")

artist_table_insert = ("""INSERT INTO 
                        artists(artist_id, name, location, latitude, longitude)
                        VALUES(%s,%s,%s,%s,%s);""")


time_table_insert = ("""INSERT INTO 
                    time(start_time, hour, day, week, month, year, weekday)
                    VALUES(%s,%s,%s,%s,%s,%s,%s);""")

# FIND SONGS

song_select = ("""SELECT s.song_id, a.artist_id 
                FROM songs AS s
                LEFT OUTER JOIN artists AS a ON s.artist_id = a.artist_id
                WHERE s.title = %s AND a.name = %s AND s.duration = %s;
                """)


# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]