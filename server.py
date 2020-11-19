import flask
from flask import abort
from voice_buffer import VoiceBuffer
from denoiser_interface import Denoiser
import sys

app = flask.Flask(__name__)
# Default gives 4 Users, from 1 to 4
app.buffers = {
    '1': VoiceBuffer(),
    '2': VoiceBuffer(),
    '3': VoiceBuffer(),
    '4': VoiceBuffer(),
} # Could be changed with user API
app.model = Denoiser('models/model.pkl')

@app.route("/users", methods=["GET"])
def list_users():
    """GET request to users end-point returns list of users"""
    users = list(flask.current_app.buffers.keys())
    return flask.jsonify(users=users, status=1)

@app.route("/users", methods=["PUT"])
def new_user():
    """
    PUT request with uid param to users end-point:
    - Creates user buffer with uid
    - returns list of all users after creation of the new user
    """
    try:
        uid = flask.request.args['uid']
    except KeyError:
        error_message = """
        PUT Request to users end-point creates a new user.
        No uid parameter providing user name was found.
        """
        abort(400, error_message)
    flask.current_app.buffers[uid] = VoiceBuffer()
    users = list(flask.current_app.buffers.keys())
    return flask.jsonify(users=users, status=1)

@app.route("/users", methods=["DELETE"])
def delete_user():
    """
    DELETE request with uid param to users end-point:
    - Removes the user buffer with provided uid if exists.
    - returns list of all users in all cases
    - returned status is 1 if success, 0 if uid not found
    """
    try:
        uid = flask.request.args['uid']
    except KeyError:
        error_message = """
        DELETE Request to users end-point deletes an existing user.
        No uid parameter providing user name was found.
        """
        abort(400, error_message)
    try:
        flask.current_app.buffers.pop(uid)
        status = 1
    except KeyError:
        status = 0
    users = list(flask.current_app.buffers.keys())
    return flask.jsonify(users=users, status=status)

@app.route("/users", methods=["POST"])
def update_user():
    """
    POST request with uid_old and uid_new params to users end-point:
    - Deletes old user buffer with uid_old
    - Creates new user buffer with uid_new
    - returns list of all users after renaming the user even if user not found
    - status is 1 if success, 0 if user not found
    WARNING: buffer is lost
    """
    try:
        uid_old = flask.request.args['uid_old']
        uid_new = flask.request.args['uid_new']
    except KeyError:
        error_message = """
        POST Request to users end-point updates an existing user.
        You need to provide uid_old and uid_new params.
        """
        abort(400, error_message)
    try:
        flask.current_app.buffers.pop(uid_old)
        status = 1
    except KeyError:
        status = 0
    flask.current_app.buffers[uid_new] = VoiceBuffer()
    users = list(flask.current_app.buffers.keys())
    return flask.jsonify(users=users, status=status)


@app.route("/denoise", methods=["POST"])
def denoise():
    raw_data = flask.request.get_data()
    uid = flask.request.args.get('uid')
    sid = flask.request.args.get('sid')
    flask.current_app.buffers[uid].append(raw_data)
    if flask.current_app.buffers[uid].is_full:
        batch = flask.current_app.buffers[uid].flush()
        batch = flask.current_app.model.denoise(batch)
        return flask.jsonify(uid=uid, sid=sid, data=batch.tolist(), status=2)
    else:
        return flask.jsonify(uid=uid, sid=sid, data=[], status=1)

@app.route("/reset", methods=["POST"])
def reset():
    uid = flask.request.args.get('uid')
    flask.current_app.buffers[uid].reset()
    return flask.jsonify(uid=uid, sid=-1, data=[], status=1)

@app.route("/flush", methods=["POST"])
def flush():
    uid = flask.request.args.get('uid')
    sid = flask.request.args.get('sid')
    batch = flask.current_app.buffers[uid].flush()
    batch = flask.current_app.model.denoise(batch)
    return flask.jsonify(uid=uid, sid=sid, data=batch.tolist(), status=2)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = 8080
    app.run(host="0.0.0.0", port=port)
