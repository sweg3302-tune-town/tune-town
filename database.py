from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def connect_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

# Method to fetch data from the database
def addPost(data):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Example query
        # query = "INSERT INTO your_table_name (column1, column2, column3) VALUES (%s, %s, %s)"
        query = "INSERT INTO posts (column1, column2, column3) VALUES (%s, %s, %s)"

        cursor.execute(query, data)
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print("Error adding data to database:", e)
        return False
    
# ADD USER - DONE
def addUser(username):
    try:
        connection = connect_db()
        print("--CONNECTED--")
        cursor = connection.cursor()
        print("cursor working")

        db_check = "SELECT * FROM users WHERE username = %s"
        cursor.execute(db_check, (username,))
        exsisting_user = cursor.fetchone()

        if exsisting_user:
            print("User already in database.")
        else:
            insert_user = "INSERT INTO users (username) VALUES (%s)"
            cursor.execute(insert_user, (username,))
            connection.commit()
            print("This new user has been added to the database!")

        # Close cursor and connection
        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print("Error adding user into database:", e)
        return False
