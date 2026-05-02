from flask import Flask

app = Flask(__name__)

app.config.from_object('config.Config')

# import database initializer
from app.models import initialize_database

# run it once when server starts
initialize_database()

from app import routes