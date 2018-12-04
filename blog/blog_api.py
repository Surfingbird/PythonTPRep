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

    def create_users(self, users_info):
        """
        Creates users. Has to be committed after creation.
        """
        users_info_hashed = []
        for user_info in users_info:
            if not all(user_info):
                raise ValueError('Login or password is blank')
            user_info[1] = md5(user_info[1].encode()).hexdigest()
            users_info_hashed.append(user_info)
        query = """
              INSERT INTO Users (Login, Password)
              VALUES (%s, %s);
              """
        self.cursor.executemany(query, users_info_hashed)

    def auth(self, login, password):
        """
        Authorises user. If user exists, adds him to self.auth_users
        """
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
        """
        Return all registered users
        """
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
        """
        Creates blog. Has to be committed after creation.
        """
        if not name:
            raise ValueError('Blank blog name.')

        author_id = author_id or 'NULL'
        self.cursor.execute(f"""
                        INSERT INTO Blogs (Name, AuthorID)
                        VALUES ('{name}', {author_id});
                        """)

    def edit_blog(self, blog_id, name):
        """
        Edits blog name. Has to be committed after editing.
        """
        if not name:
            raise ValueError('Blank blog name.')

        self.cursor.execute(f"""
                        UPDATE Blogs
                        SET Name = '{name}'
                        WHERE BlogID = {blog_id};
                        """)

    def delete_blog(self, blog_id):
        """
        Deletes blog. Has to be committed after deletion.
        """
        if not blog_id:
            raise ValueError('Blank blog_id')

        self.cursor.execute(f"""
                        DELETE FROM Blogs
                        WHERE BlogID = {blog_id};
                        """)

    def get_blogs_all(self):
        """
        Returns names of all blogs
        """
        self.cursor.execute("""
                        SELECT Name
                        FROM Blogs;
                        """)
        result = self.cursor.fetchall()
        return [b[0] for b in result]

    def get_blogs_auth(self):
        """
        Returns names of all blogs created by authorised users
        """
        self.cursor.execute("""
                        SELECT Name
                        FROM Blogs
                        WHERE AuthorID IS NOT NULL;
                        """)
        result = self.cursor.fetchall()
        return [b[0] for b in result]

    def create_post(self, blog_ids, author_id, header, content):
        """
        Creates post in given blogs. Has to be committed after creation.
        """
        if not any([blog_ids, author_id, header, content]):
            raise ValueError('Blank blog_ids, author_id, header or content.')

        for blog_id in blog_ids:
            self.cursor.execute(f"""
                            INSERT INTO Posts (BlogID, AuthorID, Header, Content)
                            VALUES ({blog_id}, {author_id}, '{header}', '{content}');
                            """)

    def edit_post(self, post_id, header, content):
        """
        Edits header and content in post by its ID. Has to be committed after edition.
        """
        if not any([post_id, header, content]):
            raise ValueError('Blank post_id, header or content.')

        self.cursor.execute(f"""
                        UPDATE Posts
                        SET Header = '{header}', Content = '{content}'
                        WHERE PostID = {post_id};
                        """)

    def delete_post(self, post_id):
        """
        Deletes post by its ID. Has to be committed after deletion.
        """
        if not post_id:
            raise ValueError('Blank post_id.')

        self.cursor.execute(f"""
                        DELETE FROM Posts
                        WHERE PostID = {post_id};
                        """)

    def add_comment(self, post_id, author_id, content, parent_id=None):
        """
        Creates comment if user is authorised and returns its comment_id. Has to be committed after creation.
        """
        if author_id not in self.auth_users:
            raise Exception(f'User is not authorised. (UserID = {author_id})')
        if not any([post_id, author_id, content]):
            raise ValueError('Blank post_id, author_id or content.')

        parent_id = parent_id or 'NULL'
        self.cursor.execute(f"""
                        INSERT INTO Comments (PostID, AuthorID, ParentID, Content)
                        VALUES ({post_id}, {author_id}, {parent_id}, '{content}');
                        """)

        self.cursor.execute('SELECT LAST_INSERT_ID();')
        comment_id, = self.cursor.fetchone()
        return comment_id

    def get_comments_by_user_from_post(self, post_id, author_id):
        """
        Returns comments made by user from specified post
        """
        if not any([post_id, author_id]):
            raise ValueError('Blank post_id or author_id.')

        self.cursor.execute(f"""
                        SELECT Content
                        FROM Comments
                        WHERE PostID = {post_id} AND AuthorID = {author_id};
                        """)
        return self.cursor.fetchall()

    def get_comment_thread(self, comment_id):
        """
        Returns comment thread starting with specified comment_id.
        Uses breadth-first search.
        """
        if not comment_id:
            raise ValueError('Blank comment_id.')

        stack = []
        queue = []

        self.cursor.execute(f"""SELECT CommentID, PostID, AuthorID, ParentID, Content
                                FROM Comments
                                WHERE CommentID = {comment_id}""")
        comment_info = self.cursor.fetchone()
        queue.insert(0, comment_info)
        while queue:
            comment_info = queue.pop()
            stack.append(comment_info)
            comment_id = comment_info[0]
            self.cursor.execute(f"""SELECT CommentID, PostID, AuthorID, ParentID, Content
                                FROM Comments
                                WHERE ParentID = {comment_id}""")
            comments = self.cursor.fetchall()
            for comment_info in comments:
                queue.insert(0, comment_info)

        return stack

    def get_comments_by_users_from_blog(self, user_ids, blog_id):
        """
        Returns comments made by several users from specified blog.
        """
        if not any([user_ids, blog_id]):
            raise ValueError('Blank user_ids or blog_id.')

        user_ids_str = str(tuple(user_ids))
        self.cursor.execute(f"""
                        SELECT c.CommentID, c.PostID, c.AuthorID, c.ParentID, c.Content
                        FROM Comments AS c
                        LEFT JOIN Posts AS p
                        ON c.PostID = p.PostID
                        WHERE p.BlogID = {blog_id} AND c.AuthorID IN {user_ids_str}
                        """)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()
