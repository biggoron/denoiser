import flask
from voice_buffer import VoiceBuffer
from denoiser_interface import Denoiser

app = flask.Flask(__name__)
app.buffers = [VoiceBuffer()] * 4
app.model = Denoiser('models/model.pkl')

@app.route("/denoise", methods=["POST"])
def denoise():
    raw_data = flask.request.get_data()
    uid = int(flask.request.args.get('uid'))
    sid = int(flask.request.args.get('sid'))
    flask.current_app.buffers[uid].append(raw_data)
    if flask.current_app.buffers[uid].is_full:
        batch = flask.current_app.buffers[uid].flush()
        batch = flask.current_app.model.denoise(batch)
        return flask.jsonify(uid=uid, sid=sid, data=batch.tolist(), status=2)
    else:
        return flask.jsonify(uid=uid, sid=sid, data=[], status=1)

@app.route("/reset", methods=["POST"])
def reset():
    uid = int(flask.request.args.get('uid'))
    flask.current_app.buffers[uid].reset()
    return flask.jsonify(uid=uid, sid=-1, data=[], status=1)

@app.route("/flush", methods=["POST"])
def flush():
    uid = int(flask.request.args.get('uid'))
    sid = int(flask.request.args.get('sid'))
    batch = flask.current_app.buffers[uid].flush()
    batch = flask.current_app.model.denoise(batch)
    return flask.jsonify(uid=uid, sid=sid, data=batch.tolist(), status=2)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
