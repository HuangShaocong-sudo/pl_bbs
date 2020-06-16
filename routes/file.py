import os

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
)

from routes import *
from models.fileindex import FileIndex
from models.college import College
from werkzeug.datastructures import FileStorage

main = Blueprint('file', __name__)


@main.route('/')
def index():
    user = current_user()

    college_id = int(request.args.get('c_id', -1))
    if college_id == -1:
        files = FileIndex.all(college_id=1)
    else:
        files = FileIndex.all(college_id=college_id)

    colleges = College.all()
    return render_template('file/index.html', login_user=user, cs=colleges, fs=files)


@main.route('/upload', methods=['POST'], strict_slashes=False)
def upload():
    file: FileStorage = request.files['myfile']
    suffix = file.filename.split('.')[-1]

    if suffix not in ['txt', 'pdf', 'png', 'jpg', 'xls', 'JPG','PNG', 'xlsx', 'gif', 'GIF', 'doc', 'docx', 'ppt', 'pptx']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        localname = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('upload', localname)
        file.save(path)

        college_id = request.form.to_dict()['college_id']
        u = current_user()
        form = dict(
            filename=file.filename,
            localname=localname,
            user_id=u.id,
            college_id=college_id,
        )
        FileIndex.new(form)

    return redirect('.?c_id=%s' % college_id)


@main.route('/download/<filename>')
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        else:
            abort(404)
