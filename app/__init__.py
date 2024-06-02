from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models
from app import user_routes
from app import admin_routes