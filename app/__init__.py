# -*- coding: utf-8 -*-

from flask import Flask
from config import load_config

app = Flask(__name__, instance_relative_config=True)

from app import views


config = load_config()
app.config.from_object(config)
