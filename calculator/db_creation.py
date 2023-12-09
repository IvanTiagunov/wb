import psycopg2
import pandas as pd
from sqlalchemy import create_engine

db_params = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'Olofmeister1337',
    'database': 'wildberries_commissions'
}

excel_file_path = 'C:\\Users\\лл\\Downloads\\table.xlsx'
try:
    connection = psycopg2.connect(**db_params)
    df = pd.read_excel(excel_file_path)
    engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')
    df.to_sql('commissions', engine, index=False, if_exists='replace')
    print("Таблица успешно создана.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    if connection:
        connection.close()
        print("Соединение с базой данных закрыто.")