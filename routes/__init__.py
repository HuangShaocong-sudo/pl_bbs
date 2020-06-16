import uuid
from functools import wraps

import redis
from flask import (
    request,
    abort,
    current_app,
    redirect,
    url_for,
)

from models.user import User
from utils import log


cache = redis.StrictRedis()


# def current_user():
#     if 'session_id' in request.cookies:
#         session_id = request.cookies['session_id']
#         s = Session.one_for_session_id(session_id=session_id)
#         key = 'session_id_{}'.format(session_id)
#         user_id = int(cache.get(key))
#         log('current_user key <{}> user_id <{}>'.format(key, user_id))
#         u = User.one(id=user_id)
#         return u
#     else:
#         return None


def current_user():
    # uid = session.get('user_id', '')
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        key = 'session_id_{}'.format(session_id)
        if cache.exists(key):
            uid = int(cache.get(key))
            u = User.one(id=uid)
            return u
    else:
        return None


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        if cache.exists(token):
            user_id = int(cache.get(token))
            u = current_user()
            if user_id == u.id:
                cache.delete(token)
                return f(*args, **kwargs)
            else:
                abort(401)
        else:
            abort(401)
        # if token in csrf_tokens and csrf_tokens[token] == u.id:
        #     csrf_tokens.pop(token)
        #     return f(*args, **kwargs)
        # else:
        #     abort(401)
    return wrapper


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if u is not None:
            return f(*args, **kwargs)
        else:
            abort(403)

    return wrapper


def new_csrf_token():
    u = current_user()
    if u is not None:
        token = str(uuid.uuid4())
        # csrf_tokens[token] = u.id
        cache.set(token, u.id)
        return token
    # return ''


def validate_register(form: dict):
    validate = False
    result = ''
    name = form['username']
    if [True for e in form.values() if e == '']:
        result = '输入不能为空'
    elif len(name) < 2:
        result = '用户名长度不能小于2'
    elif '@' not in form['mail']:
        result = '请输入正确的邮箱'
    elif User.one(username=name) is not None:
        result = '用户名已存在'
    else:
        validate = True
        result = '请前往邮箱进行验证'
    return validate, result


def login_direct(u):
    # session 中写入 user_id
    session_id = str(uuid.uuid4())
    key = 'session_id_{}'.format(session_id)
    cache.set(key, u.id)

    # 响应里 set_cookie
    redirect_to_index = redirect(url_for('.index'))
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('session_id', value=session_id)

    # 转到主页面
    return response
