from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


def active_sort(topics):
    topics.sort(key=lambda t: t.last_active_time, reverse=True)
    return topics


@main.route("/")
def index():
    user = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1 or board_id == 1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    ms = active_sort(ms)
    bs = Board.all()
    return render_template(
        "topic/index.html",
        ms=ms,
        bs=bs,
        bid=board_id,
        login_user=user
    )


@main.route('/<int:id>')
def detail(id):
    user = current_user()
    m = Topic.get(id)
    # 模板中再拿 topic 的所有 reply
    token = new_csrf_token()
    log('topic token', token)
    return render_template(
        "topic/detail.html",
        topic=m,
        token=token,
        login_user=user,
    )


@main.route("/delete")
@csrf_required
def delete():
    # /delete?id=xxx&token=xxx
    # 只有owner模板中才有删除按键, 所以@owner_required 略， 有 csrf_required 就够了
    _id = int(request.args.get('id'))
    t: Topic = Topic.one(id=_id)
    if t is not None:  # 不加 if 快速点多下就不行
        for r in t.replies():
            r.delete()
        t.delete()
    return redirect(url_for('.index'))


@main.route("/new")
@login_required
def new():
    # board_id = int(request.args.get('board_id'))
    bs = Board.all()
    token = new_csrf_token()
    user = current_user()
    return render_template(
        "topic/new.html",
        bs=bs,
        token=token,
        login_user=user,
    )


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    u = current_user()
    Topic.new(form, user_id=u.id)
    return redirect(url_for('.index'))
