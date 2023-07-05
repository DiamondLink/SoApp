import os
from app import app, db

os.system("del C://Users//Baptiste//Downloads//app_db.db")

os.system("rd /s /q C://Users\Baptiste//Downloads//flask_app//migrations")

with app.app_context():
    db.create_all()

os.system("flask db init")
os.system("flask db migrate -m \"init\"")
os.system("flask db upgrade")

