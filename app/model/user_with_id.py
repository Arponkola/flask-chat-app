from app.extension import db

class Users(db.Model):
    _id = db.Column(db.Integer, primary_key=True, nullable=False) #no need to autoincrement beacause it is primary key
    name = db.Column(db.String(100), nullable=False)
    room_code = db.Column(db.String(100), nullable=False)


class Messages(db.Model):
    _id = db.Column(db.Integer, primary_key=True, nullable=False) #no need to autoincrement beacause it is primary key
    room_code = db.Column(db.String(100), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    msg = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

def create_user_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()