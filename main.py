from app import db, app, socketio
from models import Files
from api.files import files_router
from api.llm import llm_router

app.register_blueprint(files_router)
app.register_blueprint(llm_router)

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_tables()
    socketio.run(app,host="0.0.0.0", port=4321, debug=True)