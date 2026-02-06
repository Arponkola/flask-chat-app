from app import create_app
from app.extension import socketio
import os

main_app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(main_app, host="0.0.0.0", port=port)