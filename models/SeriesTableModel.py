#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.base import MyPymysql
from app import app
import pandas as pd
from pandas import DataFrame, Series
from common.util.my_sqlalchemy import sqlalchemy_engine


def SeriesTableModel(ProjID, ColumnID, ColumnEXID, TableName, Where):
    sql_info = """SELECT
                COUNT(1) SUMDATA,
                repDB.{} optID,
                CONVERT (repDB.{}, CHAR) optEXID,
                max(
                    Ifnull(optDB.optionNM, N' ')
                ) optionNM,
                max(
                    Ifnull(optDBEX.optionNM, N' ')
                ) optionEXNM
            FROM
                `{}` repDB
            INNER JOIN `b_option` optDB ON repDB.projectID = optDB.projectID
            AND optDB.columnID = '{}'
            AND Ifnull(repDB.{}, '') = optDB.optionID
            INNER JOIN b_option optDBEX ON repDB.projectID = optDBEX.projectID
            AND optDBEX.columnID = '{}'
            AND rtrim(Ifnull(repDB.{}, ' ')) <> ''
            AND 1 = optDBEX.effectFlag
            AND Ifnull(repDB.{}, '') = optDBEX.optionID
            WHERE
                {}
            GROUP BY
                repDB.{}, repDB.{}
            ORDER BY
                CONVERT (repDB.{}, SIGNED),
                CONVERT (repDB.{}, SIGNED)
            """.format(ColumnID, ColumnEXID, TableName, ColumnID, ColumnID, ColumnEXID, ColumnEXID, ColumnEXID, Where, ColumnEXID, ColumnID, ColumnEXID, ColumnID)


    sql_data = """
                SELECT
                    AVG(
                        CONVERT (
                            Ifnull(repDB1.{}, 0),
                            DECIMAL (20, 8)
                        )
                    ) avgdata,
                    SUM(
                        CONVERT (
                            Ifnull(repDB1.{}, 0),
                            DECIMAL (20, 8)
                        )
                    ) SUMALL,
                    STDDEV_SAMP(
                        CONVERT (
                            Ifnull(repDB1.{}, 0),
                            DECIMAL (20, 8)
                        )
                    ) STDEVALL,
                    COUNT(1) SUMDATA,
                    repDB1.{} optEXID,
                    max(
                        Ifnull(optDBEX1.optionNM, N' ')
                    ) optionEXNM
                FROM
                    `{}` repDB1
                INNER JOIN b_option optDBEX1 ON optDBEX1.projectID = repDB1.projectID
                AND optDBEX1.columnID = '{}'
                AND rtrim(Ifnull(repDB1.{}, ' ')) <> ''
                AND 1 = optDBEX1.effectFlag
                AND Ifnull(repDB1.{}, '') = optDBEX1.optionID
                WHERE
                    {}
                GROUP BY
                    repDB1.{}
                ORDER BY
                    CONVERT (optEXID, SIGNED)
                """.format(ColumnID, ColumnID, ColumnID, ColumnEXID, TableName, ColumnEXID, ColumnEXID, ColumnEXID, Where, ColumnEXID)
    ret = MyPymysql('mysql')
    info_data = ret.selectall_sql(sql_info)
    data = ret.selectall_sql(sql_data)
    # print info_data
    # print data
    ret.close()
    return info_data, data

def SeriesSubOptModel(ProjID, columnID):
    ret = MyPymysql('mysql')
    sql = "select optionID, optionNM from `b_option` where projectID={} AND columnID='{}' AND effectFlag=1 ORDER BY CONVERT (optionID, SIGNED);".format(ProjID, columnID)
    data = ret.selectall_sql(sql)
    ret.close()
    return data

if __name__ == '__main__':
    # SeriesTableModel(7, 'P2Q01', 'ZYDM', 'dc_bys2016_dataandusers', '1=1')
    print SeriesSubOptModel(7, "P2Q01")