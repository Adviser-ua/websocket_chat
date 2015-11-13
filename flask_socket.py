# coding=UTF-8
# script create by Konstantyn Davidenko
# mail: kostya_ya@it-transit.com
#

"""
specification
"""

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('my event', namespace='/ws')
def test_message(message):
    print 'event'
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/')
def test_message(message):
    print 'bc event'
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/')
def test_connect():
    print 'conn'
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, port=9090)