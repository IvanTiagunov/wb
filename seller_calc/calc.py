from datetime import timedelta, date, datetime
import time

import psycopg2
import schedule
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def calculations():
    conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT)
    cursor = conn.cursor()

    # Получение сегодняшней и вчерашней даты
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # SQL-запрос для вычисления разности qty для уникальных nm_id
    sql_query = f"""
        SELECT nm_id, SUM(CASE WHEN date::date = '{today}' THEN -qty ELSE qty END) AS difference, AVG(price), '{today}'
        FROM amount
        WHERE date::date IN ('{today}', '{yesterday}')
        GROUP BY nm_id
    """

# Выполнение SQL-запроса
    cursor.execute(sql_query)

    # Получение результатов
    results = cursor.fetchall()
    sql_insert_query = "INSERT INTO sellercalculations (articul, sells, cost, date) VALUES (%s, %s, %s, %s)"
    cursor.executemany(sql_insert_query, results)
    conn.commit()
    sql_query_update = f"""
        UPDATE sellercalculations
        SET sells = 0
        WHERE sells < 0"""
    cursor.execute(sql_query_update)
    conn.commit()
    cursor.close()
    conn.close()
    print("did calculations")


def start_calc():
    # Планирование выполнения обновления каждый день в определенное время (здесь приведен пример для 12:00)
    schedule.every().day.at("05:00").do(calculations)

    # Запуск планировщика
    while True:
        schedule.run_pending()
        time.sleep(1)


def temp_update_minus_sells():
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT)
    cursor = conn.cursor()

    sql_query_update = f"""
            UPDATE sellercalculations
            SET sells = sells * -1
            WHERE sells < 0"""
    cursor.execute(sql_query_update)
    conn.commit()
    cursor.close()


if __name__ == "__main__":
    #schedule_update()
    calculations()
    #temp_update_minus_sells()