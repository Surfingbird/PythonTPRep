import pymysql.cursors
from hashlib import md5
import configparser


class BlogAPI:
    def __init__(self, path_to_config=None):
        path_to_config = path_to_config or 'settings.config'
        config = configparser.ConfigParser()
        config.read(path_to_config)
        host = config.get('Settings', 'host')
        user = config.get('Settings', 'user')
        password = config.get('Settings', 'password')
        database = config.get('Settings', 'database')
        port = config.get('Settings', 'port')

        self.conn = pymysql.connect(host=host,
                                    port=int(port),
                                    database=database,
                                    user=user,
                                    password=password)
        self.cursor = self.conn.cursor()
        self.auth_users = []

    def create_user(self, login, password):
        if not (login and password):
            raise ValueError('Login or password is blank')

        hashed_pwd = md5(password.encode()).hexdigest()
        self.cursor.execute(f"""
                            INSERT INTO Users (Login, Password)
                            VALUES ('{login}', '{hashed_pwd}');
                            """)

    def auth(self, login, password):
        if not (login and password):
            raise ValueError('Login or password is blank')

        hashed_pwd = md5(password.encode()).hexdigest()

        self.cursor.execute(f"""
                            SELECT UserID 
                            FROM Users
                            WHERE Login = '{login}' AND Password = '{hashed_pwd}';
                            """)
        result = self.cursor.fetchone()
        if result:
            user_id, = result
            self.auth_users.append(user_id)

    def get_users(self):
        self.cursor.execute("""
                            SELECT Login
                            FROM Users;
                            """)
        user = self.cursor.fetchone()
        all_users = []
        while user:
            username, = user
            all_users.append(username)
            user = self.cursor.fetchone()
        return all_users

    def create_blog(self, name, author_id=None):
        if not name:
            raise ValueError('Blank blog name.')

        author_id = author_id or 'NULL'
        self.cursor.execute(f"""
                            INSERT INTO Blogs (Name, AuthorID)
                            VALUES ('{name}', {author_id});
                            """)

    def edit_blog(self, blog_id, name):
        if not name:
            raise ValueError('Blank blog name.')

        self.cursor.execute(f"""
                            UPDATE Blogs
                            SET Name = '{name}'
                            WHERE BlogID = {blog_id};
                            """)

    def delete_blog(self, blog_id):
        if not blog_id:
            raise ValueError('Blank blog_id')

        self.cursor.execute(f"""
                            DELETE FROM Blogs
                            WHERE BlogID = {blog_id};
                            """)

    def get_blogs_all(self):
        self.cursor.execute("""
                            SELECT Name
                            FROM Blogs;
                            """)
        result = self.cursor.fetchall()
        return [b[0] for b in result]

    def get_blogs_auth(self):
        self.cursor.execute("""
                            SELECT Name
                            FROM Blogs
                            WHERE AuthorID IS NOT NULL;
                            """)
        result = self.cursor.fetchall()
        return [b[0] for b in result]

    def create_post(self, blog_ids, author_id, header, content):
        if not any([blog_ids, author_id, header, content]):
            raise ValueError('Blank blog_ids, author_id, header or content.')

        for blog_id in blog_ids:
            self.cursor.execute(f"""
                                INSERT INTO Posts (BlogID, AuthorID, Header, Content)
                                VALUES ({blog_id}, {author_id}, '{header}', '{content}');
                                """)

    def edit_post(self, post_id, header, content):
        if not any([post_id, header, content]):
            raise ValueError('Blank post_id, header or content.')

        self.cursor.execute(f"""
                            UPDATE Posts
                            SET Header = '{header}', Content = '{content}'
                            WHERE PostID = {post_id};
                            """)

    def delete_post(self, post_id):
        if not post_id:
            raise ValueError('Blank post_id.')

        self.cursor.execute(f"""
                            DELETE FROM Posts
                            WHERE PostID = {post_id};
                            """)

    def add_comment(self, post_id, author_id, content, parent_id=None):
        if author_id not in self.auth_users:
            raise Exception(f'User is not authorised. (UserID = {author_id})')
        if not any([post_id, author_id, content]):
            raise ValueError('Blank post_id, author_id or content.')

        parent_id = parent_id or 'NULL'
        self.cursor.execute(f"""
                            INSERT INTO Comments (PostID, AuthorID, ParentID, Content)
                            VALUES ({post_id}, {author_id}, {parent_id}, '{content}');
                            """)

    def get_comments_by_user_from_post(self, post_id, author_id):
        if not any([post_id, author_id]):
            raise ValueError('Blank post_id or author_id.')

        self.cursor.execute(f"""
                            SELECT Content
                            FROM Comments
                            WHERE PostID = {post_id} AND AuthorID = {author_id};
                            """)
        return self.cursor.fetchall()

    def get_comment_thread(self, comment_id):
        if not comment_id:
            raise ValueError('Blank comment_id.')

        # RECURSEVLY GETS COMMENTS STARTING FROM COMMENT_ID
        self.cursor.execute(f"""
                            WITH RECURSIVE cte AS (
                              SELECT *
                              FROM Comments
                              WHERE PostID = (SELECT PostID 
                                FROM Comments
                                WHERE CommentID = {comment_id})
                              AND AuthorID = (SELECT AuthorID 
                                FROM Comments
                                WHERE CommentID = {comment_id})
                              UNION ALL
                            
                              SELECT c.*
                              FROM Comments AS c, cte
                              WHERE c.PostID = cte.PostID AND c.ParentID = cte.AuthorID
                            )
                            SELECT * FROM cte;
                            """)
        return self.cursor.fetchall()

    def get_comments_by_users_from_blog(self, user_ids, blog_id):
        if not any([user_ids, blog_id]):
            raise ValueError('Blank user_ids or blog_id.')

        user_ids_str = str(tuple(user_ids))
        self.cursor.execute(f"""
                            SELECT p.BlogID, c.*
                            FROM Comments AS c
                            LEFT JOIN Posts AS p
                            ON c.PostID = p.PostID
                            WHERE p.BlogID = {blog_id} AND c.AuthorID IN {user_ids_str}
                            """)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()
