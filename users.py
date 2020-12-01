import flask
from flask import abort
from voice_buffer import VoiceBuffer


def get_users(buffer_size, nb_users=4, target_log_power=-12, time_filter_length=0.3):
    # Default gives 4 Users, from 1 to 4
    return {
        f'{i}': VoiceBuffer(
            buffer_size,
            target_log_power=target_log_power,
            time_filter_length=time_filter_length,
            )
        for i in range (1, 1+nb_users)
    }

def define_api(app):
    # User API
    @app.route("/users", methods=["get"])
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
        args = flask.current_app.args
        try:
            uid = flask.request.args['uid']
        except KeyError:
            error_message = """
            PUT Request to users end-point creates a new user.
            No uid parameter providing user name was found.
            """
            abort(400, error_message)
        flask.current_app.buffers[uid] = VoiceBuffer(
            args.buffer,
            target_log_power=args.target_log_power,
            time_filter_length=args.time_filter_length,
            )
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
        args = flask.current_app.args
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
        flask.current_app.buffers[uid_new] = VoiceBuffer(
            args.buffer,
            target_log_power=args.target_log_power,
            time_filter_length=args.time_filter_length,
            )
        users = list(flask.current_app.buffers.keys())
        return flask.jsonify(users=users, status=status)

    # Buffers API
    @app.route("/reset", methods=["POST"])
    def reset():
        uid = flask.request.args.get('uid')
        flask.current_app.buffers[uid].reset()
        return flask.jsonify(uid=uid, sid=-1, data=[], status=1)
