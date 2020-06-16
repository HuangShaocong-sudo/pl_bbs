import hashlib

from sqlalchemy import Column, String, Text

import config
import secret
from models.base_model import SQLMixin, db
from utils import log


class User(SQLMixin, db.Model):
    __tablename__ = 'User'
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    image = Column(String(100), nullable=False, default='/images/default.jpg')
    email = Column(String(50), nullable=False, default=config.test_mail)
    signature = Column(String(100), nullable=False, default='这家伙很懒，什么个性签名都没有留下。')

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        salted = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return salted

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        log('register', form)
        u = User.new(form)
        return u

    @classmethod
    def validate_login(cls, form):
        query = dict(
            username=form['username'],
            password=User.salted_password(form['password']),
        )
        log('validate_login', form, query)
        return User.one(**query)
