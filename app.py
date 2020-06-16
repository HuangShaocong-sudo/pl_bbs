#!/usr/bin/env python3

from flask import Flask
import time

import secret
import config
from models.base_model import db

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.mail import main as mail_routes
from routes.message import main as message_routes
from routes.wall import main as wall_routes
from routes.file import main as file_routes


def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def remove_script(content):
    # content 在用了 | safe 过滤器后，不是 str 类型
    c = str(content)
    c = c.replace('>', '&gt;')
    c = c.replace('<', '&lt;')
    # c = c.replace('script', 'removed')
    # print('remove_script after <{}>'.format(c))
    return c


def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # app.secret_key = secret.secret_key

    uri = 'mysql+pymysql://root:{}@localhost/BBS?charset=utf8mb4'.format(
        secret.database_password
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    register_routes(app)

    app.template_filter()(format_time)
    app.template_filter()(remove_script)

    # flask_admin

    return app


def register_routes(app):
    """
    在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
    蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
    用法如下sa
    """
    # 注册蓝图
    # 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/mail')
    app.register_blueprint(message_routes, url_prefix='/message')
    app.register_blueprint(wall_routes, url_prefix='/wall')
    app.register_blueprint(file_routes, url_prefix='/file')



