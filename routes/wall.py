from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.word import Word
from models.wall import Wall

main = Blueprint('wall', __name__)


@main.route("/")
def index():
    user = current_user()
    id = int(request.args.get('id', -1))
    if id == -1:
        ms = Word.all(wall_id=1)
        wall = Wall.one(id=1)
    else:
        ms = Word.all(wall_id=id)
        wall = Wall.one(id=id)
    ws = Wall.all()

    return render_template(
        "wall/index.html",
        ms=ms,
        ws=ws,
        wall=wall,
        login_user=user
    )


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    Word.new(form)
    log('add form', form)
    return redirect(url_for('.index', id=form['wall_id']))
