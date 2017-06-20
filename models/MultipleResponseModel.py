#!/usr/bin/env python
# -*- coding:utf-8 -*-
from common.base import MyPymysql

# 多重相应
def case(TableName, ColumnID, UserID, ProjectID, Where):
    ret = MyPymysql('mysql')
    # case_sql = "SELECT COUNT(1) SUMALL FROM `{}` repDBALL  WHERE {} AND rtrim(Ifnull(repDBALL.{}, '')) <> '';".format(TableName,Where,ColumnID) # yi
    case_sql = """SELECT
        COUNT(1) SUMALL from `{}` where {} in (
        SELECT
            repDBALL.{}
        FROM
            `{}` repDBALL
        INNER JOIN b_option optDB ON optDB.userID = {}
        AND optDB.projectID = {}
        AND optDB.columnID = '{}'
        AND Ifnull(repDBALL.{}, ' ') like
            CONCAT('%.', optDB.optionID, '.%')
        WHERE
            1 = 1
        AND rtrim(Ifnull(repDBALL.{}, '')) <> '');""".format(TableName, ColumnID, ColumnID, TableName, UserID, ProjectID, ColumnID, ColumnID, ColumnID)
    sumall_sql = "SELECT COUNT(1) SUMALL FROM `{}` repDBALL WHERE {};".format(TableName, Where)
    valid_sql = """
        SELECT
            COUNT(1) SUMDATA ,
            optDB.optionID optionID,
            max(
                Ifnull(optDB.optionNM, N' ')
            ) optionNM,
            max(
                Ifnull(optDB.effectFlag, 0)
            ) effectFlag
        FROM
            `{}` repDB
        INNER JOIN b_option optDB ON  optDB.userID = {}
        AND optDB.projectID = {}
        AND optDB.columnID = '{}'
        AND locate(
            CONCAT('.', optDB.optionID, '.'),
            Ifnull(repDB.{}, ' ')
        ) > 0
        WHERE {}
        GROUP BY
            optDB.optionID
        ORDER BY
            CONVERT (optDB.optionID, SIGNED)
        """.format(TableName, UserID, ProjectID, ColumnID, ColumnID, Where)

    case_data = ret.selectall_sql(case_sql)
    sumall_data = ret.selectall_sql(sumall_sql)
    valid_data = ret.selectall_sql(valid_sql)
    ret.close()
    # print case_data
    # print sumall_data
    # print valid_data
    return case_data[0], sumall_data[0], valid_data


if __name__ == '__main__':
    case("dc_bys2016_dataandusers", 'P5Q06', 6, 7, "P1Q01BDM =1")
