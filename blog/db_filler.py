from blog_api import BlogAPI
from faker import Faker
from random import randint, sample
from hashlib import md5

f = Faker()
b = BlogAPI()

hasher = lambda pwd: md5(pwd.encode()).hexdigest()
passwords = [f.password() for _ in range(1000)]
hashed_pwds = [hasher(pwd) for pwd in passwords]

user_names = set()
while len(user_names) < 1000:
    user_names.add(f.user_name())
users_info = list(zip(user_names, hashed_pwds))

b.cursor.executemany("""
                    INSERT INTO Users (Login, Password)
                    VALUES (%s, %s);
                    """, users_info)
b.commit()

for user_name, password in zip(user_names, passwords):
    b.auth(login=user_name, password=password)

blogs_info = []
auth_blogs_amount = randint(0, 100)
author_ids = sample(b.auth_users, auth_blogs_amount)
for i in range(auth_blogs_amount):
    name = f.sentence(nb_words=3)
    author_id = str(author_ids.pop())
    blogs_info.append((name, author_id))
for _ in range(100 - auth_blogs_amount):
    name = f.sentence(nb_words=3)
    author_id = None
    blogs_info.append((name, author_id))
b.cursor.executemany("""
                     INSERT INTO Blogs (Name, AuthorID)
                     VALUES (%s, %s);
                     """, blogs_info)
b.commit()

posts_info = []
while len(posts_info) < 10000:
    blog_ids = sample(range(100), randint(1, 3))
    author_id = b.auth_users[randint(0, 999)]
    header = f.sentence(nb_words=4)
    content = f.text(max_nb_chars=200, ext_word_list=None)
    for blog_id in blog_ids:
        posts_info.append((str(blog_id), str(author_id), header, content))
b.cursor.executemany("""
                     INSERT INTO Posts (BlogID, AuthorID, Header, Content)
                     VALUES (%s, %s, %s, %s);
                     """, posts_info)
b.commit()


def add_answers(post_id, levels_left, last_id, parent_id=None):
    if levels_left == 0:
        return last_id, []
    comments = []
    if parent_id:
        parent_id = str(parent_id)
    answers_amount = randint(0, 3)
    for _ in range(answers_amount):
        answerer_id = str(b.auth_users[randint(0, 999)])
        answer = f.sentence(nb_words=7)
        comments.append((str(post_id), answerer_id, parent_id, answer))
        last_id += 1
        last_id, new_comments = add_answers(post_id=post_id,
                                            levels_left=levels_left - 1, last_id=last_id, parent_id=last_id)
        comments += new_comments
    return last_id, comments


last_comment_id = b.add_comment(post_id=1, author_id=1,
                                content='I need CommentID of first comment added by me '
                                        'in case there are already are comments in table. '
                                        'I need this to create comments with proper parent id')

comments = []
while len(comments) < 100000:
    max_nesting_level = randint(1, 4)
    post_id = randint(1, 10000)
    last_comment_id, new_comments = add_answers(post_id=post_id, levels_left=max_nesting_level,
                                                last_id=last_comment_id)
    comments += new_comments

b.cursor.executemany("""
                     INSERT INTO Comments (PostID, AuthorID, ParentID, Content)
                     VALUES (%s, %s, %s, %s);
                     """, comments)
b.commit()
