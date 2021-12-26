from extension import db
from datetime import datetime

# 创建网站基本配置
class ConfigModel(db.Model):
    __tablename__ = 'webconfig'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(200),nullable=True)
    subhead = db.Column(db.String(200),nullable=True)
    keyword = db.Column(db.Text,nullable=True)
    description = db.Column(db.Text,nullable=True)
    author = db.Column(db.String(200),nullable=True)
    author_referral = db.Column(db.Text,nullable=True)
    email = db.Column(db.String(100))
    number_pages = db.Column(db.Integer,nullable=True)
    copyright = db.Column(db.String(100),nullable=True)
    information = db.Column(db.Text)
    Whitea_list = db.Column(db.String(200))
# 创建导航条
class NavModel(db.Model):
    __tablename__ = 'navigation_bar'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    nav_name = db.Column(db.String(200))
    nav_href = db.Column(db.String(200))
    state = db.Column(db.Integer,nullable=False,default=1)

# 创建文章
class articleModel(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    article_title = db.Column(db.String(255),nullable=False)
    article_content = db.Column(db.Text,nullable=False)
    article_img = db.Column(db.String(200))
    article_introduce = db.Column(db.String(255),nullable=False)
    article_show = db.Column(db.Integer,default=1)
    article_encryption = db.Column(db.Integer,default=1)
    encryption_code = db.Column(db.String(100))
    Access_number = db.Column(db.Integer,default=1)
    datetime = db.Column(db.DateTime,default=datetime.now)
    nav_bar_id = db.Column(db.Integer,db.ForeignKey('navigation_bar.id'))
    navbar = db.relationship('NavModel', backref="articles")

# 创建管理员用户
class UserAdminModel(db.Model):
    __tablename__ = 'useradmin'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(200),nullable=False)
    name = db.Column(db.String(200),nullable=False)
    state = db.Column(db.Integer,nullable=False,default=1)
    type = db.Column(db.String(10),nullable=False)

# 创建友情链接
class blogrollModel(db.Model):
    __tablename__ = 'blogroll'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(200),nullable=False)
    href = db.Column(db.String(200),nullable=False)
    state = db.Column(db.Integer,nullable=False,default=1)