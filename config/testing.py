# -*- coding: utf-8 -*-

from default import Config

class TestingConfig(Config):
    DEBUG = True
    MYSQL_HOST = "123.57.145.24:3306"
    MYSQL_USER = "analy"
    MYSQL_PASSWORD = "Wp-123456"
    MYSQL_DB = "anadata"
