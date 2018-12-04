from blog_api import BlogAPI
from faker import Faker

b = BlogAPI()
f = Faker()


print(len(b.get_blogs_all()), b.get_blogs_all())
print(len(b.get_blogs_auth()), b.get_blogs_auth())
b.create_post([1, 2, 3], 1, 'Kek', 'Testovich')
b.commit()
b.edit_post(945, 'Hotdoog', 'Liska-sosiska и Саша-Горчится')
b.commit()
b.delete_post(945)
b.commit()
print(b.get_comments_by_user_from_post(2180, 239))
print(b.get_comment_thread(1626))
print(b.get_comments_by_users_from_blog([12, 34, 56], 12))
