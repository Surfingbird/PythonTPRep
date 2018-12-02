import pymysql
import configparser

path_to_config = 'settings.config'
config = configparser.ConfigParser()
config.read(path_to_config)
host = config.get('Settings', 'host')
user = config.get('Settings', 'user')
password = config.get('Settings', 'password')
database = config.get('Settings', 'database')
port = config.get('Settings', 'port')

conn = pymysql.connect(host=host,
                       port=int(port),
                       user=user,
                       password=password)
cursor = conn.cursor()
cursor.execute(f'DROP DATABASE IF EXISTS {database};')
cursor.execute(f'CREATE DATABASE {database};')
cursor.execute(f'USE {database};')
cursor.execute("""
                CREATE TABLE Users(
                UserID INT(11) AUTO_INCREMENT NOT NULL,
                Login VARCHAR(32) UNIQUE NOT NULL,
                Password VARCHAR(32) NOT NULL,
                PRIMARY KEY(UserID)
                );
                """)
cursor.execute("""
                CREATE TABLE Blogs(
                BlogID INT(11) AUTO_INCREMENT NOT NULL,
                Name VARCHAR(64) NOT NULL,
                AuthorID INT(11) DEFAULT NULL,
                PRIMARY KEY(BlogID)
                );
                """)
cursor.execute("""
                CREATE TABLE Posts(
                PostID INT(11) AUTO_INCREMENT NOT NULL,
                BlogID INT(11) NOT NULL,
                AuthorID INT(11) NOT NULL,
                Header VARCHAR(64) NOT NULL,
                Content TEXT NOT NULL,
                PRIMARY KEY(PostID)
                );
                """)

cursor.execute("""
                CREATE TABLE Comments(
                CommentID INT(11) AUTO_INCREMENT NOT NULL ,
                PostID INT(11) NOT NULL,
                AuthorID INT(11) NOT NULL,
                ParentID INT(11) DEFAULT NULL,
                Content TEXT NOT NULL ,
                PRIMARY KEY(CommentID)
                );
                """)
# Creating index for BlogID in Posts
# for speeding up searches in methods:
# - get_comment_thread
# - get_comments_by_user_from_post
cursor.execute("CREATE INDEX BlogID ON Posts(BlogID);")

# Creating index for PostID in Blogs
# for speeding up searches in methods:
# - get_comments_by_users_from_blog
# - edit_blog
# - delete_blog
cursor.execute("CREATE INDEX PostID ON Comments(PostID);")
conn.close()
