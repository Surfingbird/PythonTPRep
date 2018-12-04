from blog_api import BlogAPI
from faker import Faker
from random import randint, sample

f = Faker()
b = BlogAPI()

passwords = [f.password() for _ in range(1000)]
user_names = set()
while len(user_names) < 1000:
    user_names.add(f.user_name())
users_info = [list(user) for user in zip(user_names, passwords)]

b.create_users(users_info=users_info)
b.commit()

for user_name, password in zip(user_names, passwords):
    b.auth(login=user_name, password=password)

auth_blogs = randint(0, 100)
author_ids = sample(b.auth_users, auth_blogs)
for i in range(auth_blogs):
    name = f.sentence(nb_words=3)
    b.create_blog(name=name, author_id=author_ids[i])
for _ in range(100 - auth_blogs):
    name = f.sentence(nb_words=3)
    b.create_blog(name=name)
b.commit()

posts = 0
while posts < 10000:
    blog_ids = sample(range(100), randint(1, 3))
    posts += len(blog_ids)
    author_id = b.auth_users[randint(0, 999)]
    header = f.sentence(nb_words=4)
    content = f.text(max_nb_chars=200, ext_word_list=None)
    b.create_post(blog_ids=blog_ids,
                  author_id=author_id,
                  header=header,
                  content=content)
b.commit()


def add_answers(post_id, levels_left, parent_id=None):
    if levels_left == 0:
        return 0
    parent_id = parent_id or 'NULL'
    answers_amount = randint(0, 3)
    for _ in range(answers_amount):
        answerer_id = b.auth_users[randint(0, 999)]
        answer = f.sentence(nb_words=7)
        comment_id = b.add_comment(post_id=post_id, parent_id=parent_id, author_id=answerer_id, content=answer)
        answers_amount += add_answers(parent_id=comment_id, post_id=post_id, levels_left=levels_left - 1)
    return answers_amount


comments = 0
while comments < 100000:
    max_nesting_level = randint(1, 4)
    post_id = randint(1, 10000)
    comments += add_answers(post_id=post_id, levels_left=max_nesting_level)
b.commit()
