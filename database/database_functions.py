from configparser import ConfigParser

try:
    from .create import create_connection
except ImportError:
    from create import create_connection
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
    sql_query = (
        """SELECT word FROM user_words where user_id =%s ORDER BY id DESC limit 1;"""
    )

    return run_query(sql_query, [user_id])


def get_users():
    sql_query = """SELECT email FROM users;"""
    return run_query(sql_query)


def get_user_data(user_id):
    sql = """SELECT d.input_word,u.word
    FROM user_words u LEFT JOIN 
    user_data d
    ON u.word = d.word
    WHERE u.user_id = %s"""
    return run_query(sql, [user_id])

def insert_into_logs(username, text, is_bot=False):
    """

    :param username:
    :param text:
    :param: is_bot:
    :return:
    """
    sql_query = (
        """INSERT into conversation_log(username,is_bot,convo) VALUES(%s,%s,%s)"""
    )
    run_query(sql_query, [username, is_bot, text])

def get_conversation(username):
    """

    :param username:
    :return: return all previous conversation for the user
    """
    sql_query = """select * from conversation_log where username = %s"""
    return run_query(sql_query, [username])


if __name__ == "__main__":
    print(get_users())
