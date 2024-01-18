import psycopg2
import pandas as pd
import config
from sqlalchemy import create_engine

db_params = {
    'host': '158.160.15.205',
    'port': '5432',
    'user': 'admin',
    'password': 'admin',
    'database': 'wb'
}


try:
    connection = psycopg2.connect(**db_params)
    engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE SellerCalculations (id SERIAL PRIMARY KEY, articul INTEGER,  sells INTEGER, cost INTEGER)")
    connection.commit()
    cursor.close
    print("Таблица успешно создана.")
except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    if connection:
        connection.close()
        print("Соединение с базой данных закрыто.")