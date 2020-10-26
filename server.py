import flask
from voice_buffer import VoiceBuffer
from denoiser_interface import Denoiser

app = flask.Flask(__name__)
app.buffers = [VoiceBuffer()] * 4
app.model = Denoiser('model.pkl')

@app.route("/denoise", methods=["GET"])
def denoise():
    raw_data = flask.request.get_data()
    uid = int(flask.request.args.get('uid'))
    sid = int(flask.request.args.get('sid'))
    flask.current_app.buffers[uid].append(raw_data)
    if flask.current_app.buffers[uid].is_full:
        batch = flask.current_app.buffers[uid].flush()
        batch = flask.current_app.model.denoise(batch)
        return flask.jsonify(sid=sid, data=str(batch), status=2)
    else:
        return flask.jsonify(sid=sid, data="", status=1)

@app.route("/reset", methods=["GET"])
def reset():
    uid = int(flask.request.args.get('uid'))
    flask.current_app.buffers[uid].reset()
    return flask.jsonify(data="", status=1)

@app.route("/flush", methods=["GET"])
def flush():
    uid = int(flask.request.args.get('uid'))
    sid = int(flask.request.args.get('sid'))
    batch = flask.current_app.buffers[uid].flush()
    batch = flask.current_app.model.denoise(batch)
    return flask.jsonify(sid=sid, data=str(batch), status=2)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
