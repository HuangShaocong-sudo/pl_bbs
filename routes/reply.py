from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    Request)

from models.message import Message
from routes import *

from models.reply import Reply
from models.topic import Topic


main = Blueprint('reply', __name__)


def users_from_content(content):
    # 内容 @123 内容
    # 如果用户名含有空格 就不行了 @name 123
    parts = content.split()
    users = []

    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.one(username=username)
            log('users_from_content <{}> <{}> <{}>'.format(username, p, parts))
            if u is not None and u not in users:
                users.append(u)

    return users


def send_message(sender, receivers, reply):
    u = Topic.one(id=reply.topic_id).user()
    if u is not sender and u not in receivers:
        receivers.append(u)

    log('send_message', sender, receivers, reply.content)
    for r in receivers:
        form = dict(
            topic_id=reply.topic_id,
            replier_id=sender.id,
            receiver_id=r.id,
            content=reply.content,
        )
        Message.new(form)


@main.route("/add", methods=["POST"])
@login_required
def add():
    form = request.form
    u = current_user()

    form = form.to_dict()
    r = Reply.new(form, user_id=u.id)

    content = form['content']
    users = users_from_content(content)
    send_message(u, users, r)

    # update last_active_time
    t_id = form['topic_id']
    t: Topic = Topic.one(id=t_id)
    t.update(t.id, last_active_time=r.created_time)

    return redirect(url_for('topic.detail', id=r.topic_id))


@main.route("/delete")
@csrf_required
def delete():
    # reply/delete?id=xxx&token=xxx
    _id = int(request.args.get('id'))
    tid = int(request.args.get('tid'))
    r: Reply= Reply.one(id=_id)
    if r is not None:
        r.delete()
    return redirect(url_for('topic.detail', id=tid))
