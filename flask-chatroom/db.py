# '''
# db
# database file, containing all the logic to interface with the sql database
# '''

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from models import *

# # "database/main.db" specifies the database file
# # change it if you wish
# # turn echo = True to display sql output
# engine = create_engine("sqlite:///database/main.db", echo=False)

# # initializes the database
# Base.metadata.create_all(engine)

# # inserts a user to the database
# def insert_user(username: str, password: str):
#     with Session(engine) as session:
#         user = User(username=username, password=password)
#         session.add(user)
#         session.commit()

# # gets a user from the database
# def get_user(username: str):
#     with Session(engine) as session:
#         return session.get(User, username)
    


import sqlite3
import hashlib, uuid
ENCODING = 'utf-8'
# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise



class SQLDatabase():
    '''
        Our SQL Database

    '''
    userCount:int

    # Get the database running
    def __init__(self, database_arg="database.db"):
        self.conn = sqlite3.connect(database_arg, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.userCount = 0

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------

    
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='1'):

        # Clear the database if needed



        self.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='Users'")
        usersExists = self.cur.fetchone()
        # Create the users table
        self.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            Id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            salt TEXT,
            admin INTEGER DEFAULT 0
        )   
        """)


        self.commit()

        
        if usersExists != None:
            self.execute("SELECT id FROM Users ORDER BY id DESC LIMIT 1")
            row = self.cur.fetchone()
            self.userCount = row[0];    
        else:
            self.userCount += 1
        # Add our admin user
            self.add_user(self.userCount, 'admin', admin_password, admin=1)



        

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, id, username, password, admin=0):
        sql_cmd = """
            INSERT INTO Users
            VALUES({id}, '{username}', '{password}', '{salt}', {admin})
        """


        salt = uuid.uuid4().hex
        hashedPassword = hashlib.sha512(password.encode(ENCODING) + salt.encode(ENCODING)).hexdigest()
        sql_cmd = sql_cmd.format(id = id, username=username, password=hashedPassword,salt = salt,admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    #-----------------------------------------------------------------------------


    def register_check(self, username:str, password:str, admin=0):


        sqlQuery= f"""SELECT 1 FROM Users WHERE username = '{username}'"""
        self.execute(sqlQuery)
        if self.cur.fetchone():
            return True
        else:
            self.userCount += 1
            self.add_user(self.userCount, username, password)
            return False


    def get_user(self, username:str):
        sqlQuery= f"""SELECT 1 FROM Users WHERE username = '{username}'"""
        self.execute(sqlQuery)
        if self.cur.fetchone():
            return True
        else:
            return False
        



    def get_friends(self, username:str):
        sqlQuery = f"""SELECT * FROM Friends WHERE username = '{username}'"""
        self.execute(sqlQuery)
        rowReturned = self.cur.fetchone()
        friends = rowReturned[1]
        friends.split(",")
        if isinstance(friends, str):
            ls = [friends]
            return ls
        return friends

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = f"""SELECT * FROM Users WHERE username = '{username}'"""

        
        self.execute(sql_query)
       
        rowReturned = self.cur.fetchone()
        # If our query returns
        if rowReturned:
            retreivedPassword = rowReturned[2]
            salt = rowReturned[3]
            enteredPasswordHashed = hashlib.sha512(password.encode(ENCODING) + salt.encode(ENCODING)).hexdigest()
            if str(enteredPasswordHashed) == retreivedPassword:
                return True
            else:
                return False
        else:
            return False    
