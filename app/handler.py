from .extension import db, socketio
from flask import Blueprint, render_template, session, request, redirect, url_for
from flask_socketio import join_room, leave_room, send, emit
import random
from .model.user_with_id import Users, Messages
from string import ascii_letters

app_bp = Blueprint(
    "handler", __name__,
    static_folder='static',
    template_folder='template'
)


def create_room_code(length):
    codes = Users.query.all()
    all_codes = []
    
    for code in codes:
        all_codes.append(code.room_code)
    
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_letters).upper()
        
        if code not in all_codes:
            return code

@app_bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        action = request.form.get('action')
        
        if not name:
            return render_template("home.html", error="name is required")
        
        if action == "create":
            session['user'] = name
            session['room'] = create_room_code(6)
    
            user = Users(name=name, room_code=session['room'])
            db.session.add(user)
            db.session.commit()
            
            return redirect(url_for('handler.chat'))
        
        room_codes = Users.query.all()
        
        rooms = []
        
        for room in room_codes:
            rooms.append(room.room_code)
        
        if code not in rooms:
            return render_template("home.html", error=f"No room present of this code : '{code}'")
        
        if action=='join' and code in rooms:
            session['user'] = name
            session['room'] = code
            return redirect(url_for("handler.chat", name=session['user'], room=session["room"]))
        
        return render_template("home.html", error="room code is required for join in room")
        
    return render_template("home.html")


@app_bp.route('/chat', methods=['GET'])
def chat():
    if 'user' not in session or 'room' not in session:
        return "access deined"
    
    room = session["room"]
    user = session["user"]
    
    return render_template("chat_room.html", name=user, room=room)


@socketio.on('connect')
def connect():
    if "user" not in session or "room" not in session:
        return False
    
    room_exists = Users.query.filter_by(room_code=session.get("room")).first()
    
    if not room_exists:
        pass
    
    name = session["user"]
    room = session["room"]
    join_room(room)
    
    history = Messages.query.filter_by(
        room_code=room
    ).order_by(Messages.timestamp).all()
    
    for m in history:
        emit("message", {
            "user" : m.name,
            "msg" : m.msg
        })
    
    existing_user = Users.query.filter_by(
        name=name,
        room_code=room
    ).first()
    
    if not existing_user:
        db.session.add(Users(name=name, room_code=room))
        db.session.commit()
    
    data = {
        "user" : name,
        "room" : room,
        "msg" : "join the room"
    }
    emit('message', data ,to=room)
    

@socketio.on('message')
def handle_message(msg:str):
    msg = msg.strip()
    
    if not msg:
        return
    
    user = session.get("user")
    room_code = session.get("room")
    
    try:
        message = Messages(
            room_code = room_code,
            name = user,
            msg = msg
        )
        db.session.add(message)
        db.session.commit()
    except Exception as e:
        print(e)

    data = {
        "user" : session["user"],
        "room" : session["room"],
        "msg" : msg
    }
    
    emit(
        'message',
        data,
        to=data["room"]
    )
    
@socketio.on('disconnect')
def disconnect():
    if "user" not in session and "room" not in session:
        return
    name = session["user"]
    room = session['room']
    
    user = Users.query.filter_by(name=name, room_code=room).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    leave_room(room)
    
    remaining_users = Users.query.filter_by(room_code=room).count()
    
    data = {
        "user" : name,
        "room" : room,
        "msg" : "left the room"
    }
    
    if remaining_users==0:
        Messages.query.filter_by(room_code=room).delete()
        db.session.commit()
        # print(f"Room {room} deleted (no users left)")
    
    else:
        emit('message', data , to=room)
    
    # print('Disconnected')