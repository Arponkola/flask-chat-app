#import necessary libraiies
from flask import Flask
from . import handler
from .extension import db, bcrypt, socketio
from .model import user_with_id
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chat_user.db"
    app.config["SQLALCHEMY_TRACKBACK_MODIFICATION"] = False
    app.secret_key = 'my-secret-key'
    
    user_with_id.create_user_db(app)
            
    bcrypt.init_app(app)
    socketio.init_app(app)
    print(app.secret_key)
    
    app.register_blueprint(blueprint=handler.app_bp, uri_prefix='/')
    
    return app