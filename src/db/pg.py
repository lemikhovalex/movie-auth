from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config.db import PG_DB_NAME, PG_PASSWORD, PG_USER_NAME

db = SQLAlchemy()


def init_db(app: Flask):
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://{user}:{pasword}@{host}/{db_name}".format(
        user=PG_USER_NAME,
        pasword=PG_PASSWORD,
        db_name=PG_DB_NAME,
        host="db",
    )
    db.init_app(app)
