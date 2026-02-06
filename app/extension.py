from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
socketio = SocketIO()
bcrypt = Bcrypt()