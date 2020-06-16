from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Message

main = Blueprint('message', __name__)


@main.route('/')
@login_required
def message():
    user = current_user()
    messages = Message.all(receiver_id=user.id)
    read = [m for m in messages if m.read == 1]
    unread = [m for m in messages if m.read == 0]

    for m in messages:
        m.update(m.id, read=1)
    return render_template(
        "user/message.html",
        login_user=user,
        unread=unread,
        read=read,
    )
