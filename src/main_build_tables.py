import os

import psycopg2
import requests
from psycopg2.extras import DictCursor

# create sql alchemy
# app.app_context().push()
print(os.environ.get("POSTGRES_DB"))
with psycopg2.connect(
    dbname=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host="db",
    cursor_factory=DictCursor,
) as pg_conn:

    # register user as request
    response = requests.post(
        "http://auth:5000/api/v1/users/",
        json={
            "credentials": {"login": "admin", "password": "admin"},
            "user_data": {"first_name": "13", "second_name": "Est"},
        },
    )
    admin_id = response.json()["user_id"]

    # give him admin role

    with pg_conn.cursor() as cursor:
        query = "INSERT INTO users_roles  (user_id, role_id) VALUES (%s);"
        try:
            cursor.execute(
                query,
                [
                    (
                        "b14e4bac-3717-4682-b1e2-f34b42d49c97",
                        0,
                    ),
                ],
            )
        except Exception as exc_insert:
            print(str(exc_insert))
