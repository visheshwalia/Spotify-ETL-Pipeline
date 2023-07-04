#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta, datetime 
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from Spotify_API import song

default_args = {
    'owner': 'vishesh',
    'depends_on_past': False,
    'start_date': datetime(2023,6,29),
    'email': ['vishesh.walia@outlook.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'Spotify_API_DAG',
    default_args=default_args,
    description='Spotify ETL process 1-min',
    schedule_interval= timedelta(minutes=60),
)



def fetch_liked_songs():
    api = song()
    api.callRefresh()
    dictionary = api.user_liked_tracks()
    return {'dictionary': dictionary}

fetch_liked = PythonOperator(
    task_id="fetch_liked_songs",
    python_callable=fetch_liked_songs,
    dag=dag,
)


def connect_upload(*args, **kwargs):
    fetch_liked_output = kwargs['ti'].xcom_pull(task_ids='fetch_liked_songs')
    dictionary = fetch_liked_output['dictionary']

    postgres_hook = PostgresHook(postgres_conn_id='postgres-airflow')
    connection = postgres_hook.get_conn()

    with connection.cursor() as cursor:
        create_liked_songs_query = '''CREATE TABLE IF NOT EXISTS liked_songs (
            added_at TIMESTAMP,
            name VARCHAR(100),
            artists VARCHAR(100),
            spotify_uri VARCHAR(30) PRIMARY KEY,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INT DEFAULT 1);'''

        cursor.execute(create_liked_songs_query)

        liked_songs_query = '''SELECT spotify_uri, is_active FROM liked_songs;'''
        cursor.execute(liked_songs_query)
        liked_songs_records = cursor.fetchall()
        liked_songs_df = pd.DataFrame(liked_songs_records, columns=['spotify_uri', 'is_active'])

        print('Adding songs to the database')
        df = pd.DataFrame(dictionary)
        df_append = df[~df['spotify_uri'].isin(liked_songs_df['spotify_uri'])]
        if not df_append.empty:
            df_append['added_at'] = df_append['added_at'].str.replace('T', ' ').str.replace('Z', '')
            df_append['artists'] = df_append['artists'].astype('str')
            data = [tuple(row) for row in df_append.values]

            # Generate placeholders for the query
            placeholders = ', '.join(['%s'] * len(df_append.columns))
            
            # Build the INSERT statement
            insert_query = f"INSERT INTO liked_songs ({', '.join(df_append.columns)}) VALUES ({placeholders})"
            
            # Execute the query
            cursor.executemany(insert_query, data)
            
            # Commit the changes
            connection.commit()
            print(f'{df_append.shape[0]} new songs added to the database')

        inactive_uri_tuple = tuple(liked_songs_df.loc[(liked_songs_df['is_active'] == 1) & (~liked_songs_df['spotify_uri'].isin(df['spotify_uri'])), 'spotify_uri'])
        if len(inactive_uri_tuple) != 0:
            placeholders = ', '.join(['%s'] * len(inactive_uri_tuple))
            is_active_0_query = f"UPDATE liked_songs SET is_active = 0, last_modified = CURRENT_TIMESTAMP WHERE spotify_uri IN ({placeholders});"
            cursor.execute(is_active_0_query, inactive_uri_tuple)
            connection.commit()
            print(f'{len(inactive_uri_tuple)} songs removed from liked songs')

        active_uri_tuple = tuple(liked_songs_df.loc[(liked_songs_df['is_active'] == 0) & (liked_songs_df['spotify_uri'].isin(df['spotify_uri'])), 'spotify_uri'])
        if len(active_uri_tuple) != 0:
            placeholders = ', '.join(['%s'] * len(active_uri_tuple))
            is_active_1_query = f"UPDATE liked_songs SET is_active = 1, last_modified = CURRENT_TIMESTAMP WHERE spotify_uri IN ({placeholders});"
            cursor.execute(is_active_1_query, active_uri_tuple)
            connection.commit()
            print(f'{len(active_uri_tuple)} songs added back again to liked songs')

connect_db = PythonOperator(
    task_id="connect_upload",
    python_callable=connect_upload,
    provide_context = True,
    dag=dag,
)


fetch_liked >> connect_db # set dependencies


