#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.base import MyPymysql

def frequency_get(UserID, ProjID, QuesID, ColumnID, ColumnName, TableName, Where):
    ret = MyPymysql('mysql')
    if Where != True:
        sql = "SELECT {}, Count(1) AS DataCount FROM {}  GROUP BY {} Order by {} Asc".format(ColumnID, TableName,
                                                                                             ColumnID, ColumnID)
    else:
        sql = "SELECT {}, Count(1) AS DataCount FROM {} WHERE GROUP BY {} Order by {} Asc".format(ColumnID,
                                                                                                  TableName,
                                                                                                  # -----问题
                                                                                                  ColumnID,
                                                                                       ColumnID)


    OptionSql = "SELECT optionNM, effectFlag, optionID FROM {} WHERE `userID`={} AND `projectID`={} AND `columnID`='{}';".format("b_option", UserID, ProjID, ColumnID)  # 暂时缺quesID



    res = ret.selectall_sql(sql)
    print res
    res1 = ret.selectall_sql(OptionSql)

    print res1

    MidSql = "SELECT {} FROM {} Order by {} Asc;".format(ColumnID, TableName, ColumnID)
    res2 = ret.selectall_sql(MidSql)
    print res2
    li = []
    for i in res2:
        li.append(i[ColumnID])
    print li

    if len(li) % 2 == 0:
        print (li[len(li)/2] + li[len(li)/2-1]) /2
    else:
        print li[len(li)/2]



    ret.close()


def test(ColumnID, TableName):
    ret = MyPymysql('mysql')
    ave_std_n_sql = """SELECT
                    	AVG(
                    		CONVERT (
                    			Ifnull(`{}`, 0),
                    			DECIMAL (16, 4)
                    		)
                    	) avgdata,
                    	STDDEV_SAMP(
                    		CONVERT (
                    			Ifnull(`{}`, 0),
                    			DECIMAL (16, 4)
                    		)
                    	) STDEVALL,
                    	COUNT(1) SUMDATA
                    FROM
                    	{} db
                    INNER JOIN B_option optDB ON optDB.projectID = 7
                    AND optDB.columnID = '{}'
                    AND Ifnull(`{}`, 0) = optDB.optionID
                    AND optDB.effectFlag = 1
                    WHERE
                    	rtrim(Ifnull(`{}`, '')) <> ''

                    """.format(ColumnID, ColumnID, TableName, ColumnID, ColumnID, ColumnID)
    res = ret.selectall_sql(ave_std_n_sql)
    print res


def test1():
    ret = MyPymysql('mysql')
    ColumnID = "P2Q02"
    TableName = "dc_bys2016_dataandusers"
    Where = "1=1"
    sumsql = "SELECT SUM(`{}`) AS sumdata, MAX(`{}`) AS maxdata,MIN(`{}`) AS mindata,AVG(`{}`) AS avgdata,STDDEV(`{}`) AS stddata FROM `{}` WHERE {};" \
        .format(ColumnID, ColumnID, ColumnID, ColumnID, ColumnID, TableName, Where)
    DataCount = ret.selectone_sql(sumsql)
    print DataCount

    ret.close()

from pandas import DataFrame
DataFrame().median()

if __name__ == '__main__':
    # frequency_get("6", "7", "0", "P2Q01", "", "dc_bys2016_dataandusers", "")
    # test("P2Q01", "dc_bys2016_dataandusers")
    # test1()
    for i in range(10):
        if i+1 == 10:
            break
        print i + 1