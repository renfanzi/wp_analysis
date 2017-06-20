#!/usr/bin/env python
# -*- coding:utf-8 -*-


from common.base import MyPymysql
from app import app
import pandas as pd
from pandas import DataFrame, Series
from common.util.my_sqlalchemy import sqlalchemy_engine


def MeanModel(ColumnID, ColumnName, TableName, Where):



    ret = MyPymysql('mysql')
    sumsql = "SELECT COUNT(1) as cnt ,SUM(`{}`) AS sumdata, MAX(`{}`) AS maxdata,MIN(`{}`) AS mindata,AVG(`{}`) AS avgdata,STDDEV(`{}`) AS stddata FROM `{}` WHERE {};" \
        .format(ColumnID, ColumnID, ColumnID, ColumnID, ColumnID, TableName, Where)
    sumdata = ret.selectone_sql(sumsql)

    MidSql = "SELECT {} FROM {} Order by {} Asc;".format(ColumnID, TableName, ColumnID)
    MidRes = ret.selectall_sql(MidSql)
    modesql = "select `{}`, count(1) as ab from `{}` where {} group by `{}` order by ab desc;".format(ColumnID,
                                                                                                      TableName, Where,
                                                                                                      ColumnID)
    modeData = ret.selectall_sql(modesql)
    ret.close()
    return sumdata, MidRes, modeData