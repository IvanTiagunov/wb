from datetime import timedelta, date, datetime
import time

import psycopg2
import schedule


def calculations():
    conn = psycopg2.connect(
            database="wb",
            user="admin",
            password="admin",
            host="158.160.15.205",
            port="5432")
    cursor = conn.cursor()

    # Получение сегодняшней и вчерашней даты
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # SQL-запрос для вычисления разности qty для уникальных nm_id
    sql_query = f"""
        SELECT nm_id, SUM(CASE WHEN date::date = '{today}' THEN qty ELSE -qty END) AS difference, AVG(price)
        FROM amount
        WHERE date::date IN ('{today}', '{yesterday}')
        GROUP BY nm_id
    """

# Выполнение SQL-запроса
    cursor.execute(sql_query)

    # Получение результатов
    results = cursor.fetchall()
    sql_insert_query = "INSERT INTO sellercalculations (articul, sells, cost) VALUES (%s, %s, %s)"
    cursor.executemany(sql_insert_query, results)
    conn.commit()
    sql_query_update = f"""
        UPDATE sellercalculations
        SET sells = sells * -1"""
    cursor.execute(sql_query_update)
    conn.commit()
    cursor.close()
    conn.close()
    print("did calculations")


def Update():
    conn = psycopg2.connect(
        database="wb",
        user="admin",
        password="admin",
        host="158.160.15.205",
        port="5432")
    cursor = conn.cursor()

    # Получение сегодняшней и вчерашней даты
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # SQL-запрос для вычисления разности qty для уникальных nm_id
    sql_query = f"""
            SELECT nm_id, SUM(CASE WHEN date::date = '{today}' THEN qty ELSE -qty END) AS difference
            FROM amount
            WHERE date::date IN ('{today}', '{yesterday}')
            GROUP BY nm_id
        """
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for row in results:
        nm_id, difference = row
        update_query = f"UPDATE sellercalculations SET sells = {difference*-1}  WHERE articul = '{nm_id}'"
        cursor.execute(sql_query)
        conn.commit()
    cursor.close()
    conn.close()

def schedule_update():
    # Планирование выполнения обновления каждый день в определенное время (здесь приведен пример для 12:00)
    schedule.every().day.at("05:00").do(Update)

    # Запуск планировщика
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_update()