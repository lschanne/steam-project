from sqlalchemy import create_engine

from constants import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_USER,
)

def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{MYSQL_USER}@{MYSQL_HOST}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
