from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def connect_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, cursorclass=pymysql.cursors.DictCursor)

connect_db()

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
    
# Route to add a new user
# @app.route('/add_user', methods=['POST'])
# def add_user(username):

#     # # Check if username is provided
#     # if not username:
#     #     return jsonify({'message': 'Username is required'}), 400

#     # Check if the username already exists
#     if User.query.filter_by(username=username).first():
#         return jsonify({'message': 'Username already exists'}), 400

#     # Create a new user object
#     new_user = User(username=username)

#     # Add the user to the session and commit changes to the database
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({'message': 'User added successfully'}), 201
