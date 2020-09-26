from configparser import ConfigParser
from .create import create_connection
import pymysql

parser = ConfigParser()
parser.read("dev.ini")
db_name = parser.get("db", "db_name")


def run_query(query, args=[], conn=None):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param query: a SQL query
    :return:
    """
    if not conn:
        conn = create_connection(db_name)
    with conn.cursor() as cursor:
        if query.lower().strip().startswith("select"):
            cursor.execute(query=query, args=args)
            return cursor.fetchall()
        else:
            # print(query, args)
            cursor.execute(query=query, args=args)
    try:
        conn.commit()
    except Exception as e:
        print("ERROR OCCURED WHILE DB COMMIT --- DB_UTILS: 43", e)


def insert_into_users(email):
    sql_update_users_table = """INSERT INTO users (email) VALUES (%s);"""
    run_query(sql_update_users_table, [email])


def get_user(email):
    sql_update_users_table = """SELECT id from users where email=%s;"""
    return run_query(sql_update_users_table, [email])


def insert_into_user_data(user_id, word, input_word):
    sql = """INSERT INTO user_data (user_id, word,input_word) VALUES (%s,%s,%s);"""
    run_query(sql, [user_id, word, input_word])


def insert_into_user_words(user_id, word):
    sql = """INSERT INTO user_words (user_id,word) VALUES (%s,%s);"""
    run_query(sql, [user_id, word])


def get_last_user_word(user_id):
    sql_query = """SELECT word FROM user_words where user_id =%s ORDER BY id DESC limit 1;"""

    return run_query(sql_query, [user_id])


if __name__ == "__main__":
    print(get_last_user_word(1))
