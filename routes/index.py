import os
import uuid

import gevent
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app,
)
from flask_sqlalchemy import SQLAlchemy

from werkzeug.datastructures import FileStorage

from models.base_model import db
from models.reply import Reply
from models.topic import Topic
from models.user import User

import json
from routes import *
from models.mail import send_mail
from tasks import send_async_simple
from config import admin_mail
from utils import log

from xml.sax.saxutils import unescape

main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    return redirect(url_for('.home'), code=301)


@main.route("/home")
def home():
    login_user = current_user()
    return render_template(
        "home.html",
        login_user=login_user
    )


@main.route("/login_view")
def login_view():
    return render_template("login.html")


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    validate, result = validate_register(form)  # 简单的注册条件
    if validate:
        key = str(uuid.uuid4())
        # cache.set(key, json.dumps('new user'))
        cache.set(key, 'new user')
        username = form['username']
        password = User.salted_password(form['password'])
        url = 'https://www.piggiesland.com/register/validate'
        content = '{}?token={}&username={}&password={}'.format(url, key, username, password)
        # send_mail(
        #     subject='注册验证',
        #     author=admin_mail,
        #     to=form['mail'],
        #     content='请点击链接完成注册：\n {}'.format(content),
        # )
        send_async_simple.delay(
            subject='注册验证',
            author=admin_mail,
            to=form['mail'],
            plain='请点击链接完成注册：\n {}'.format(content),
        )
        return render_template("login.html", result=result, validate=validate)
    else:
        return render_template("login.html", result=result, validate=validate)


@main.route("/register/validate")
def register_validate():
    key = request.args.get('token')
    # if cache.exists(key) and json.loads(cache.get(key)) == 'new user':
    if cache.exists(key) and cache.get(key) == b'new user':
        cache.delete(key)
        form = dict(
            username=request.args.get('username'),
            password=request.args.get('password'),
        )  # 或许该改为 form 在 cache 存取
        log('new register form', form)
        u = User.register(form)
        response = login_direct(u)
        return response
    else:
        abort(401)


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        log('login error', form)
        return redirect(url_for('.login_view'))
    else:
        response = login_direct(u)
        return response


@main.route("/logout")
@login_required
def logout():
    session_id = request.cookies['session_id']
    key = 'session_id_{}'.format(session_id)
    log('logout session_id', key)
    if cache.exists(key):
        cache.delete(key)
    return redirect(url_for('.index'))
    # return redirect(url_for('.login_view'))


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # 原本有 n+1 问题的普通写法 和 写进 redis 的写法都抛弃了
    # join 面向数据库编程
    ts = Topic.query\
        .join(Reply, Topic.id==Reply.topic_id)\
        .filter(Reply.user_id==user_id)\
        .all()
    return ts
    #
    # k = 'replied_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     rs = Reply.all(user_id=user_id)
    #     ts = []
    #     for r in rs:
    #         t = Topic.one(id=r.topic_id)
    #         ts.append(t)
    #
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #
    #     return ts


@main.route('/user/<string:username>')
def user_detail(username):
    """
    按 username 看用户信息页, 不需要身份验证
    """
    login_user = current_user()
    u = User.one(username=username)
    log('running user_detail route')
    if u is None:
        abort(404)
    else:
        # u 创建的topic
        created = created_topic(user_id=u.id)
        # u 参与的topic
        replied = replied_topic(user_id=u.id)
        return render_template(
            'user/user.html',
            login_user=login_user,
            u=u,
            created=created,
            replied=replied
        )


@main.route('/image/add', methods=['POST'])
@login_required
def avatar_add():
    file: FileStorage = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg', 'png']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.user_detail', username=u.username))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全
    return send_from_directory('images', filename)


@main.route('/setting')
@login_required
def setting():
    user = current_user()
    token = new_csrf_token()
    return render_template("user/setting.html", login_user=user, token=token)


@main.route('/setting/update', methods=['POST'])
# @login_required
@csrf_required
def setting_update():
    u = current_user()
    if u is not None:
        form = request.form.to_dict()
        User.update(u.id, **form)
        return redirect(url_for('.setting'))
    else:
        abort(403)


@main.route('/password/update', methods=['POST'])
@csrf_required
def password_update():
    u = current_user()
    form = request.form.to_dict()
    if User.salted_password(form['old_pass']) == u.password:
        password = User.salted_password(form['new_pass'])
        User.update(u.id, password=password)
        return redirect(url_for('.setting'))
    else:
        abort(401)


@main.route('/forgot')
def reset_view():
    login_user = current_user()

    return render_template(
        "user/forgot.html",
        login_user=login_user,
        result=''
    )


@main.route('/forgot/send', methods=['POST'])
def forgot_send():
    login_user = current_user()

    form = request.form.to_dict()
    # log('forgot form', form)
    u = User.one(**form)
    if u is not None:
        result = 'send'
        token = str(uuid.uuid4())
        cache.set(token, json.dumps(u.username))
        url = 'https://www.piggiesland.com/forgot/reset'
        content = "{}?token={}&username={}".format(url, token, u.username)
        log('forgot send', content, 'cache_set', cache.get(token))
        # send_mail(
        #     subject='忘记密码',
        #     author=admin_mail,
        #     to=u.email,
        #     content='点击链接重置密码：\n {}'.format(content),
        # )
        send_async_simple.delay(
            subject='忘记密码',
            author=admin_mail,
            to=u.email,
            content='点击链接重置密码：\n {}'.format(content),
        )
    else:
        result = 'error'

    return render_template(
        "user/forgot.html",
        login_user=login_user,
        result=result
    )


@main.route('/forgot/reset')
def forgot_reset():
    login_user = current_user()

    key = request.args.get('token')
    username = request.args.get('username')
    # log('reset form', cache.exists(key), key, username)

    if cache.exists(key) and json.loads(cache.get(key)) == username:
        result = 'reset'
        return render_template(
            "user/forgot.html",
            login_user=login_user,
            result=result,
            token=key,
        )
    else:
        abort(401)


@main.route('/forgot/update', methods=['POST'])
def forgot_update():
    login_user = current_user()

    form = request.form.to_dict()
    key = request.args.get('token')
    username = json.loads(cache.get(key))

    u = User.one(username=username)
    if u is not None:
        result = 'updated'
        log('forgot update user: ', u.username)
        password = User.salted_password(form['new_pwd'])
        u.update(u.id, password=password)
        cache.delete(key)
        return render_template(
            "user/forgot.html",
            login_user=login_user,
            result=result
        )
    else:
        abort(401)
