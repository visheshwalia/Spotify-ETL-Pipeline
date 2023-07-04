## Docker-ETL-Pipeline
Data Pipelines Using Python, PostgreSQL, Apache Airflow, and Docker

This data pipeline utilizes Spotify's API to fetch and update a user's liked tracks in a PostgreSQL database. It is scheduled to run every hour using Apache Airflow. To ensure a clean and isolated environment, I have deployed the database and Apache Airflow in separate Docker containers, avoiding any conflicts with my local system configurations.

## Python
To access Spotify's API, OAuth 2.0 protocol is employed for authorization. Since the objective is to access a user's saved tracks, the "authorization flow" is utilized, which involves an additional level of complexity compared to the "client credentials" flow. The primary reason for choosing this flow is to obtain both the access token and the refresh token. As the original access token has a short lifespan (typically 60 minutes), I have implemented code to retrieve a new access token each time the code interacts with the API.

## Postgres
Based on the API response, one of the following three actions occurs:
1.	If a new track is added to the user's playlist, a new record is appended to the database, and the 'is_active' flag is set to 1 by default.
2.	If a track is removed from the playlist, the 'is_active' flag for that track is set to 0, and the 'last_modified' column is updated with the current timestamp.
3.	If a track is added again but was previously in the playlist, the 'is_active' flag is set to 1, and the 'last_modified' column is updated with the current timestamp.

## Airflow
To ensure the pipeline keeps running smoothly, Apache Airflow is utilized within a Docker container. To meet the specific requirements of the project, a custom Docker image was created, including the necessary Python packages. The code is scheduled to run every hour using Apache Airflow's task scheduler.

In Apache Airflow, two tasks have been defined. The first task refreshes the access token and fetches data from the Spotify API. The second task connects to the PostgreSQL database and loads the fetched data from the first task into the database.

We welcome any feedback on how to improve this pipeline and make it more efficient.

Thank you!
