import flask

from argparser import get_args
# Includes user buffers and users CRUD
from users import get_users, define_api


args = get_args()
app = flask.Flask(__name__)

app.buffers = get_users(args.buffer, 4, args.target_log_power)
define_api(app)

@app.route("/normalize", methods=["POST"])
def normalize():
    raw_data = flask.request.get_data()
    uid = flask.request.args.get('uid')
    sid = int(flask.request.args.get('sid'))
    flask.current_app.buffers[uid].append(raw_data)
    if flask.current_app.buffers[uid].is_full:
        batch = flask.current_app.buffers[uid].flush()
        batch = flask.current_app.buffers[uid].normalizer.normalize(batch)
        return flask.jsonify(uid=uid, sid=sid, data=batch, status=2)
    else:
        return flask.jsonify(uid=uid, sid=sid, data=[], status=1)

@app.route("/flush", methods=["POST"])
def flush():
    uid = flask.request.args.get('uid')
    sid = int(flask.request.args.get('sid'))
    batch = flask.current_app.buffers[uid].flush()
    if len(batch) > 0:
        batch = flask.current_app.buffers[uid].normalizer.normalize(batch)
    return flask.jsonify(uid=uid, sid=sid, data=batch, status=2)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=args.port)
