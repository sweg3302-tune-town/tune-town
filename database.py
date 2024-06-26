from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DEVELOPER")
DB_PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def connect_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

# Method to fetch data from the database
# what we need:
# - delete post 
# - add friend
# - remove friend

# what is done:
# - add user
# - add post

def addPost(data):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Example query
        # query = "INSERT INTO your_table_name (column1, column2, column3) VALUES (%s, %s, %s)"
        query = "INSERT INTO posts (userId, selection, description) VALUES (%s, %s, %s)"

        cursor.execute(query, data)
        connection.commit()

        cursor.close()
        connection.close()
        
        return True

    except Exception as e:
        print("Error adding post into database:", e)
        return False
 
def addUser(username):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        db_check = "SELECT * FROM users WHERE username = %s"
        cursor.execute(db_check, (username,))
        exsisting_user = cursor.fetchone()

        if exsisting_user:
            print("User already in database.")
        else:
            query = "INSERT INTO users (username) VALUES (%s)"
            cursor.execute(query, (username,))
            connection.commit()
            print("This new user has been added to the database!")

        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print("Error adding user into database:", e)
        return False
        
    
def getMyPosts(username):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        query = "SELECT selection FROM posts WHERE userId = %s"
        cursor.execute(query, (username,))

        posts = cursor.fetchall()

        connection.commit()

        cursor.close()
        connection.close()

        return posts

    except Exception as e:
        print("Error getting user posts from database:", e)
        return []        

def getFriendPosts(username):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Query to select posts from friends
        query = """
        SELECT p.selection, p.description, p.userId
        FROM posts p
        INNER JOIN friends f ON p.userId = f.friend 
        WHERE f.user = %s
        """

        cursor.execute(query, (username,))
        posts = cursor.fetchall()

        connection.commit()

        cursor.close()
        connection.close()

        return posts

    except Exception as e:
        print("Error getting friend posts from database:", e)
        return []
    
def addFriend(user, friend):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        query = "INSERT INTO friends (user, friend) VALUES (%s, %s)"
        cursor.execute(query, (user, friend,))

        connection.commit()

        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print("Error adding friend")
        return False
        

# Database Structure Overview:
#
# Database Name: tunetown-db
#
# Tables:
# 
# 1. Table: users
#    - Description: holds all the users of the system
#    - Columns:
#      - idUser: generated id number by sql
#      - username: user's username (NOT display name)
#
# 2. Table: posts
#    - Description: holds all posts ever
#    - Columns:
#      - postId: generated id number by sql
#      - userId: the userId of the creator
#      - selection: a spotify songId
#      - description: the post caption given by the user upon post creation
#