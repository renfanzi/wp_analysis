#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.base import MyPymysql
from app import app
import pandas as pd
from pandas import DataFrame, Series
from common.util.my_sqlalchemy import sqlalchemy_engine

# 比较均值
def CompareMean(ProjID, ColumnID, ColumnEXID, TableName, Where):
    sql = """
        SELECT
            COUNT(1) SUMDATA,
            AVG(
                CONVERT (
                    Ifnull(repDB.{}, 0),
                    decimal (20, 8)
                )
            ) avgdata,
            SUM(
                CONVERT (
                    Ifnull(repDB.{}, 0),
                    decimal (20, 8)
                )
            ) SUMALL,
            STDDEV_SAMP(
                CONVERT (
                    Ifnull(repDB.{}, 0),
                    decimal (20, 8)
                )
            ) STDEVALL,
            optDB.optionID optionID,
            max(
                Ifnull(optDB.optionNM, N' ')
            ) optionNM,
            MAX(
                CONVERT (
                    Ifnull(repDB.{}, 0),
                    decimal (20, 8)
                )
            ) colMAX,
            MIN(
                CONVERT (
                    Ifnull(repDB.{}, 0),
                    decimal (20, 8)
                )
            ) colMIN
        FROM
            `{}` repDB
        INNER JOIN b_option optDB ON optDB.projectID = {}
        AND optDB.columnID = '{}'
        AND rtrim(Ifnull(repDB.{}, '')) = optDB.optionID
        AND 1 = optDB.effectFlag
        AND rtrim(Ifnull(repDB.{}, '')) <> ''
        WHERE
            {}
        GROUP BY
            optDB.optionID
        ORDER BY
            CONVERT (optionID, SIGNED)
        """.format(ColumnID, ColumnID, ColumnID, ColumnID, ColumnID, TableName, ProjID, ColumnEXID, ColumnEXID,
                   ColumnEXID, Where)
    ret = MyPymysql('mysql')
    data = ret.selectall_sql(sql)
    # print data
    ret.close()
    return data


def midValue(ProjID, ColumnID,  ColumnEXID, TableName, Where):
    sql = """
        SELECT
            optDB.optionID optionID, repDB.{} {}
        FROM
            `{}` repDB
        INNER JOIN b_option optDB ON optDB.projectID = {}
        AND optDB.columnID = '{}'
        AND rtrim(
            Ifnull(repDB.{}, '')
        ) = optDB.optionID
        AND 1 = optDB.effectFlag
        AND rtrim(
            Ifnull(repDB.{}, '')
        ) <> ''
        WHERE
        {}
        ORDER BY
            CONVERT (optionID, SIGNED),
            CONVERT ({}, decimal(20,8))
        """.format(ColumnID, ColumnID, TableName, ProjID, ColumnEXID, ColumnEXID, ColumnEXID, Where,ColumnID)
    df = pd.read_sql(sql, sqlalchemy_engine)
    df = df.dropna()
    return (df["optionID"]).dropna(), (df[ColumnID]).dropna()


#
if __name__ == '__main__':
#
    CompareMean(7, 'P4Q08', 'ZYDM', 'dc_bys2016_dataandusers', '1=1')
#     ret, id = midValue(7, 'P4Q08', 'ZYDM', 'dc_bys2016_dataandusers', '1=1')
