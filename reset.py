from sqlalchemy import create_engine

import secret
from app import configured_app
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User
from models.wall import Wall
from models.college import College
from models.fileindex import FileIndex

from utils import log

import random


def reset_database():
    # 现在 mysql root 默认用 socket 来验证而不是密码
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(
        secret.database_password
    )
    e = create_engine(url, echo=True)

    with e.connect() as c:
        # 创建 database bbs
        c.execute('DROP DATABASE IF EXISTS BBS')
        c.execute('CREATE DATABASE BBS CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE BBS')

    db.metadata.create_all(bind=e)


def generate_fake_date():
    # 测试账号
    form = dict(
        username='user1',
        password=User.salted_password('123'),
    )
    u1 = User.register(form)

    form = dict(
        username='user2',
        password=User.salted_password('123'),
        image='/images/dance.gif',
    )
    u2 = User.register(form)

    # 留言墙
    w = Wall.new({'title': '校务'})
    # w = Wall.new({'title': '树洞'})
    w = Wall.new({'title': '兼职'})
    w = Wall.new({'title': '物品'})

    # 文件分类
    c = College.new({'title': '公共'})
    c = College.new({'title': 'A学院'})
    c = College.new({'title': 'B学院'})

    # 板块
    form = dict(
        title='全部'
    )
    b = Board.new(form)

    form = dict(
        title='分享'
    )
    b = Board.new(form)

    form = dict(
        title='问答'
    )
    b = Board.new(form)

    # 帖子
    with open('markdown_demo.md', encoding='utf8') as f:
        content = f.read()

    rd_string = "一段随sfSDSD机文字大sada矿购买fda痛亏本龙Zxfasf凤你耨周xzc哈嘿"

    for i in range(5):
        log('begin topic <{}>'.format(i))
        topic_form = dict(
            title='markdown demo' + str(i),
            board_id=random.randint(2,3),
            content=content,
        )
        u_id = random.randint(1,2)
        t = Topic.new(topic_form, u_id)

        reply_form = dict(
            content='reply test',
            topic_id=t.id,
        )
        for j in range(5):
            u_id = random.randint(1, 2)
            reply_form['content'] = 'reply test' + ''.join(random.sample(rd_string,2))
            Reply.new(reply_form, u_id)

    for i in range(15):
        log('begin topic <{}>'.format(i))
        num1 = random.randint(5, 15)
        num2 = random.randint(10, 35)
        topic_form = dict(
            title=''.join(random.sample(rd_string, num1)),
            board_id=random.randint(2, 3),
            content=''.join(random.sample(rd_string, num2)),
        )
        u_id = random.randint(1, 2)
        t = Topic.new(topic_form, u_id)

        reply_form = dict(
            content='reply test',
            topic_id=t.id,
        )
        for j in range(random.randint(1, 5)):
            u_id = random.randint(1, 2)
            reply_form['content'] = 'reply test' + ''.join(random.sample(rd_string, 2))
            Reply.new(reply_form, u_id)

    # 留言

    # 文件
    form = dict(
        filename='3.gif',
        localname='3.gif',
        user_id=1,
        college_id=1,
    )
    FileIndex.new(form)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_date()
