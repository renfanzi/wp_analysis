#!/usr/bin/env python
# -*- coding:utf-8 -*-


from sqlalchemy import create_engine
import pandas as pd
from common.base import Config

ret = Config().get_content('mysql')
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(ret["user"],
                                                                               ret["password"],
                                                                               ret["host"],
                                                                               ret["port"],
                                                                               ret["db_name"])
sqlalchemy_engine = create_engine(SQLALCHEMY_DATABASE_URI,
                                  pool_size=20,
                                  pool_recycle=3600,
                                  max_overflow=10,
                                  encoding='utf-8',
                                  )


