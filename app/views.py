#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
from app import app
from flask import request, g, jsonify
from common.base import LogPath, Config

from pyvttbl import ChiSquare2way
from sqlalchemy import create_engine

import pandas as pd
from statsmodels.formula.api import ols
import statsmodels.api as sm

from common.base import MyPymysql, result
from models.MultipleResponseModel import case
from models.CompareMean import CompareMean,midValue
from models.SeriesTableModel import SeriesTableModel, SeriesSubOptModel
from models.MeanModel import MeanModel
import math
from common.util.my_sqlalchemy import sqlalchemy_engine


@app.before_first_request
def init():
    setup_logging()
    setup_db()


def setup_logging():
    ch = RotatingFileHandler(LogPath, maxBytes=10000, backupCount=20, encoding='UTF-8')
    ch.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    ch.setFormatter(logging_format)
    app.logger.addHandler(ch)


def setup_db():
    ret = Config().get_content('mysql')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(ret["user"],
                                                                                   ret["password"],
                                                                                   ret["host"],
                                                                                   ret["port"],
                                                                                   ret["db_name"])
    app.config['sqlalchemy_engine'] = create_engine(SQLALCHEMY_DATABASE_URI,
                                                    pool_size=20,
                                                    pool_recycle=3600,
                                                    max_overflow=10,
                                                    encoding='utf-8',
                                                    )


def do_chisquare2way(v1, v2):
    x2 = ChiSquare2way()
    x2.run(v1, v2)
    return {'p': x2['p'], 'df': x2['df'], 'chisq': x2['chisq'], 'N': x2['N']}


def variance(v1, v2, table, where):
    # try:
    #     sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
    #     df = pd.read_sql(sql, sqlalchemy_engine)
    #     df_dropna = df.dropna()
    #     expr = '{}~C({})'.format(v1, v2)
    #     mod = ols(expr, data=df_dropna).fit()
    #     anova_table = sm.stats.anova_lm(mod)
    #     ret = {'df': list(anova_table.df),
    #            'sum_sq': list(anova_table.sum_sq),
    #            'mean_sq': list(anova_table.mean_sq),
    #            'F': list(anova_table.F)[0],
    #            'P': list(anova_table.values.T[-1])[0]
    #            }
    # except Exception as e:
    #     app.logger.error(e)
    #     ret = {}
    # return ret

    try:
        status = 2000
        flag = 1
        sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
        df = pd.read_sql(sql, sqlalchemy_engine)
        df_dropna = df.dropna()
        expr = '{}~C({})'.format(v1, v2)
        v2sum = 0
        for i in range(len(df_dropna[v2])):
            if (df_dropna[v2]).iloc[0] == (df_dropna[v2]).iloc[i]:
                v2sum += 1
        if v2sum == len(df_dropna[v2]):
            status = 5003
            flag = 0

        if flag == 1:
            mod = ols(expr, data=df_dropna).fit()
            anova_table = sm.stats.anova_lm(mod)
            ret = {'df': list(anova_table.df),
                   'sum_sq': list(anova_table.sum_sq),
                   'mean_sq': list(anova_table.mean_sq),
                   'F': list(anova_table.F)[0],
                   'P': list(anova_table.values.T[-1])[0]
                   }
        else:
            ret = {"df": "NaN", "sum_sq": "NaN", "mean_sq": "Nan", "F": "NaN", "P": "NaN"}

    except Exception as e:
        app.logger.error(e)
        app.logger.warning(e)
        status = 4002
        ret = {"df": "NaN", "sum_sq": "NaN", "mean_sq": "Nan", "F": "NaN", "P": "NaN"}

    return ret


def chisquare2way(v1, v2, table, where):
    # sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
    # df = pd.read_sql(sql, sqlalchemy_engine)
    # df_dropna = df.dropna()
    # ret = do_chisquare2way(df_dropna[v1], df_dropna[v2])
    # return ret
    try:
        status = 2000
        flag = 1
        sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
        df = pd.read_sql(sql, sqlalchemy_engine)
        df_dropna = df.dropna()
        v2sum = 0
        for i in range(len(df_dropna[v2])):
            if (df_dropna[v2]).iloc[0] == (df_dropna[v2]).iloc[i]:
                v2sum += 1
        if v2sum == len(df_dropna[v2]):
            status = 5003
            flag = 0

        if flag == 1:
            ret = do_chisquare2way(df_dropna[v1], df_dropna[v2])
        else:
            ret = {'p': "NaN", 'df': "NaN", 'chisq': "NaN", 'N': "NaN"}

    except Exception as e:
        app.logger.error(e)
        status = 4002
        ret = {'p': "NaN", 'df': "NaN", 'chisq': "NaN", 'N': "NaN"}
    return ret


def my_4_quartiles(li):
    # 第一步：将n个变量值从小到大排列，X(j)表示此数列中第j个数。
    # 第二步：计算指数，设(n+1)P%=j+g，j为整数部分，g为小数部分。
    # 第三步：1)当g=0时：P百分位数=X(j);
    # 2)当g≠0时：P百分位数=g*X(j+1)+（1-g）*X(j)=X(j)+g*[X(j+1)-X(j)]。
    if isinstance(li, list):
        import math
        li = sorted(li)
        P1 = 0.25
        P2 = 0.5
        P3 = 0.75
        a1 = float((len(li) + 1) * P1)
        a2 = float((len(li) + 1) * P2)
        a3 = float((len(li) + 1) * P3)
        j1 = math.floor(a1)
        j2 = math.floor(a2)
        j3 = math.floor(a3)
        g1 = float(a1) - float(j1)
        g2 = float(a2) - float(j2)
        g3 = float(a3) - float(j3)
        try:
            P_value1 = g1 * li[int(j1)] + (1 - g1) * li[int(j1) - 1]
        except Exception as e1:
            P_value1 = "NaN"
        try:
            P_value2 = g2 * li[int(j2)] + (1 - g2) * li[int(j2) - 1]
        except Exception as e2:
            P_value2 = "NaN"
        try:
            P_value3 = g3 * li[int(j3)] + (1 - g3) * li[int(j3) - 1]
        except Exception as e3:
            P_value3 = "NaN"
        return (P_value1, P_value2, P_value3)
    else:
        raise IndexError


# 卡方 --(单选题)
@app.route('/v1/chisquare2way/<string:v1>:<string:v2>:<string:table>:<string:where>', methods=['GET'])
def chisquare_get(v1, v2, table, where):
    if request.method == 'GET':
        try:
            status = 2000
            flag = 1
            sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
            df = pd.read_sql(sql, app.config.get('sqlalchemy_engine'))
            df_dropna = df.dropna()
            v2sum = 0
            for i in range(len(df_dropna[v2])):
                if (df_dropna[v2]).iloc[0] == (df_dropna[v2]).iloc[i]:
                    v2sum += 1
            if v2sum == len(df_dropna[v2]):
                status = 5003
                flag = 0

            if flag == 1:
                ret = do_chisquare2way(df_dropna[v1], df_dropna[v2])
            else:
                ret = {'p': "NaN", 'df': "NaN", 'chisq': "NaN", 'N': "NaN"}

        except Exception as e:
            app.logger.error(e)
            status = 4002
            ret = {'p': "NaN", 'df': "NaN", 'chisq': "NaN", 'N': "NaN"}

        if status == 2000:
            return jsonify(ret)
        else:
            return jsonify(result(status=status, value=""))


# 方差  -- 交叉(单选或数值填空)
@app.route('/v1/variance/<string:v1>:<string:v2>:<string:table>:<string:where>', methods=['GET'])
def varianc_get(v1, v2, table, where):
    if request.method == 'GET':

        try:
            status = 2000
            flag = 1
            sql = "select {}, {} from {} where {};".format(v1, v2, table, where)
            df = pd.read_sql(sql, app.config.get('sqlalchemy_engine'))
            df_dropna = df.dropna()
            # print df_dropna[v2][-1]
            expr = '{}~C({})'.format(v1, v2)
            v2sum = 0
            for i in range(len(df_dropna[v2])):
                if (df_dropna[v2]).iloc[0] == (df_dropna[v2]).iloc[i]:
                    v2sum += 1
            if v2sum == len(df_dropna[v2]):
                status=5003
                flag = 0

            if flag == 1:
                mod = ols(expr, data=df_dropna).fit()
                anova_table = sm.stats.anova_lm(mod)
                ret = {'df': list(anova_table.df),
                                'sum_sq': list(anova_table.sum_sq),
                                'mean_sq': list(anova_table.mean_sq),
                                'F': list(anova_table.F)[0],
                                'p': list(anova_table.values.T[-1])[0]
                                }
            else:
                ret = {"df": "NaN", "sum_sq": "NaN", "mean_sq": "Nan", "F": "NaN", "P": "NaN"}

        except Exception as e:
            app.logger.error(e)
            app.logger.warning(e)
            status = 4002
            ret = {"df": "NaN", "sum_sq": "NaN", "mean_sq": "Nan", "F": "NaN", "P": "NaN"}
        if status == 2000:
            return jsonify(ret)
        else:
            return jsonify(result(status=status, value=ret))


# 频次分析--单选题
@app.route('/v1/frequency/<string:UserID>:<string:ProjID>:<string:QuesID>:<string:ColumnID>:<string:ColumnName>:<string:TableName>:<string:Where>',methods=['GET'])
def frequency_get(UserID, ProjID, QuesID, ColumnID, ColumnName, TableName, Where):
    if request.method == 'GET':
        import time
        t1 = time.time()

        try:
            status = 2000

            CountSql = "SELECT {}, Count(1) AS DataCount FROM {}  WHERE {} GROUP BY {} Order by {} Asc".format(ColumnID,
                                                                                                               TableName,
                                                                                                               Where,
                                                                                                               ColumnID,
                                                                                                               ColumnID)

            ret = MyPymysql('mysql')
            DataCount = ret.selectall_sql(CountSql)
            if len(DataCount) == False:
                status = 5002

            # 注: Effectflag {1:有效, 0:无效}
            OptionSql = "SELECT optionNM, effectFlag, optionID FROM {} WHERE userID={} AND projectID={} AND columnID='{}';".format(
                "b_option", UserID, ProjID, ColumnID)  # 暂时缺quesID

            OptionRes = ret.selectall_sql(OptionSql)

            overall_total = 0  # 整体合计
            effective_total = 0  # 有效合计 1
            missing_total = 0  # 缺失合计
            li = []
            for i in range(len(DataCount)):
                for j in range(len(OptionRes)):

                    if int(OptionRes[j]["optionID"]) == int(DataCount[i][ColumnID]) and int(
                            OptionRes[j]['effectFlag']) == 1:
                        effective_total += DataCount[i]["DataCount"]

                    else:
                        missing_total += DataCount[i]["DataCount"]

                overall_total += DataCount[i]["DataCount"]

            for k in range(len(DataCount)):
                optionNM = u"缺失"
                for v in range(len(OptionRes)):

                    if int(OptionRes[v]["optionID"]) == int(DataCount[k][ColumnID]):
                        optionNM = OptionRes[v]["optionNM"]
                        break

                countN = DataCount[k]["DataCount"]

                if effective_total:
                    PER = float(countN) / float(effective_total)
                    countPER = "%.10f" % PER

                else:
                    countPER = 0
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
                INNER JOIN B_option optDB ON optDB.projectID = {}
                AND optDB.columnID = '{}'
                AND Ifnull(`{}`, 0) = optDB.optionID
                AND optDB.effectFlag = 1
                WHERE
                    rtrim(Ifnull(`{}`, '')) <> ''
                """.format(ColumnID, ColumnID, TableName, ProjID,ColumnID, ColumnID, ColumnID)

                ave_std_n_res = ret.selectall_sql(ave_std_n_sql)

                if len(ave_std_n_res) != True:
                    status = 5002
                else:

                    average = ave_std_n_res[0]["avgdata"]
                    stdev = ave_std_n_res[0]["STDEVALL"]

                MidSql = "SELECT {} FROM {} Order by {} Asc;".format(ColumnID, TableName, ColumnID)
                midli = []
                MidRes = ret.selectall_sql(MidSql)

                for i in MidRes:
                    midli.append(i[ColumnID])
                if len(midli) % 2 == 0:
                    midValue = (float(midli[len(midli) / 2])  + float(midli[len(midli) / 2 - 1])) / 2

                else:
                    midValue = midli[len(midli) / 2]

                countTotal = effective_total
                score = average / 5 * 100

                ValueDict = {}
                ValueDict["columnID"] = ColumnID
                ValueDict["questionshortNM"] = ColumnName
                ValueDict["optionID"] = OptionRes[k]["optionID"]
                ValueDict["optionNM"] = optionNM
                ValueDict["countN"] = countN
                ValueDict["countPER"] = countPER
                ALLPER = "%.10f" % (float(countN) / float(overall_total))
                ValueDict["countALLPER"] = ALLPER  # --
                ValueDict["average"] = average
                ValueDict["stdev"] = stdev
                ValueDict["midValue"] = midValue
                ValueDict["countTotal"] = effective_total

                li.append(ValueDict)

            ret.close()
        except Exception as e:
            app.logger.error(e)
            status = 5002
            li = ""

        return jsonify(result(status, value=li))


# 均值分析 --单选和数字填空 也叫描述性统计
@app.route('/v1/mean/<string:ColumnID>:<string:ColumnName>:<string:TableName>:<string:Where>', methods=['GET'])
def mean_get(ColumnID, ColumnName, TableName, Where):
    try:
        status = 2000
        # ret = MyPymysql('mysql')
        sumdata, MidRes, modeData = MeanModel(ColumnID, ColumnName, TableName, Where)
        SendDict = {}
        SendDict["columnID"] = ColumnID
        SendDict["questionshortNM "] = ColumnName

        SendDict["countN "] = sumdata["cnt"]
        SendDict["maxValue"] = sumdata["maxdata"]
        SendDict["minValue"] = sumdata["mindata"]
        SendDict["average"] = sumdata["avgdata"]
        SendDict["stdev"] = sumdata["stddata"]
        SendDict["sum"] = sumdata["sumdata"]
        midli = []
        for i in MidRes:
            midli.append(i[ColumnID])
        if len(midli) % 2 == 0:
            midValue = midli[len(midli) / 2 ]

        else:
            midValue = (float(midli[len(midli) / 2]) + float(midli[len(midli) / 2 - 1])) / 2

        SendDict["midValue"] = midValue
        if modeData:
            modesubdata = ""
            modeflag = modeData[0][ColumnID]
            modesubdata += str(modeflag)
            for j in range(1, len(modeData)):
                if modeflag == int(modeData[j][ColumnID]):
                    modesubdata =  modesubdata + "," + str(modeData[j][ColumnID])

        else:
            modesubdata = 0
        SendDict["modeValue"] = modesubdata

    except Exception as e:
        status = 5002
        SendDict = ""
        app.logger.error(e)
    return jsonify(result(status, value=SendDict))


# 多重响应 -- ()
@app.route('/v1/multiple_response/<string:UserID>:<string:ProjID>:<string:QuesID>:<string:ColumnID>:<string:ColumnName>:<string:TableName>:<string:Where>',methods=['GET'])
def multiple_response_get(UserID, ProjID, QuesID, ColumnID, ColumnName, TableName, Where):

    try:

        case_data, sumall_data, valid_data = case(TableName, ColumnID, UserID, ProjID, Where)
        li = []
        effectivesum = 0
        for j in valid_data:
            if int(j["effectFlag"]) == 1:
                effectivesum += j["SUMDATA"]


        for i in valid_data:
            subvalue = dict()
            subvalue["optionID"] = i["optionID"]
            subvalue["optionNM"] = i["optionNM"]
            subvalue["countN"] = i["SUMDATA"]
            if int(i["effectFlag"]) == 1:
                subvalue["Flag"] = 0

                countPER = float(i["SUMDATA"]) / effectivesum
                subvalue["countPER"] = "%.10f" % countPER
            else:
                subvalue["Flag"] = 1
                countPER = float(i["SUMDATA"]) / float(sumall_data["SUMALL"])
                subvalue["countPER"] = "%.10f" % countPER
            countGEANPER = float(i["SUMDATA"]) / float(case_data["SUMALL"])
            subvalue["countGEANPER"] = "%.10f" % countGEANPER

            subvalue["sum"] = sumall_data["SUMALL"]
            subvalue["countTotal"] = effectivesum

            li.append(subvalue)

        if sumall_data["SUMALL"] - case_data["SUMALL"]:

            missvalue = dict()
            missvalue["optionID"] = ""
            missvalue["optionNM"] = u"缺失"
            missvalue["countN"] = sumall_data["SUMALL"] - case_data["SUMALL"]

            missvalue["Flag"] = 1

            countPER_qqqq = (sumall_data["SUMALL"] - case_data["SUMALL"]) / float(sumall_data["SUMALL"])
            countPER_gean = float(case_data["SUMALL"]) / float(sumall_data["SUMALL"])
            missvalue["countPER"] = "%.10f" % countPER_gean

            missvalue["countGEANPER"] = "%.10f" % countPER_qqqq

            missvalue["sum"] = sumall_data["SUMALL"]
            missvalue["countTotal"] = case_data["SUMALL"]

            li.append(missvalue)
        status = 2000
    except Exception as e:
        app.logger.error(e)
        status = 4002

    if status == 2000:
        return jsonify(li)
    else:
        return jsonify(result(status=status, value=""))



# 比较均值
@app.route('/v1/compare_mean/<string:UserID>:<string:ProjID>:<string:QuesID>:<string:ColumnID>:<string:ColumnName>:<ColumnEXID>:<string:ColumnEXName>:<string:TableName>:<string:Where>', methods=['GET'])
def CompareTheMean(UserID, ProjID, QuesID, ColumnID, ColumnName, ColumnEXID, ColumnEXName, TableName, Where):

    # try:
    status = 2000
    mean_data = CompareMean(ProjID, ColumnID, ColumnEXID, TableName, Where)
    data_li = list()

    variance_data = variance(ColumnID, ColumnEXID, TableName, Where)
    opt_id, mid_data = midValue(ProjID, ColumnID,  ColumnEXID, TableName, Where)

    for m in mean_data:
        mid_li = []
        for i in range(len(opt_id)):
            if int(m["optionID"]) == int(opt_id.iloc[i]):
                mid_li.append(mid_data.iloc[i])
        data_dict = dict()
        data_dict["columnID"] = ColumnID
        data_dict["questionshortNM"] = ColumnName
        data_dict["columnEXID"] = ColumnEXID
        data_dict["questionshortEXNM"] = ColumnEXName
        data_dict["optionEXID"] = m["optionID"]
        data_dict["optionEXNM"] = m["optionNM"]
        data_dict["countN"] = str(m["SUMDATA"])
        data_dict["average"] = m["avgdata"]
        data_dict["stdev"] = m["STDEVALL"]
        data_dict["maxValue"] = str(m["colMAX"])
        data_dict["minValue"] = str(m["colMIN"])
        data_dict["sum"] = m["SUMALL"]
        # data_dict["midValue"] = m["STDEVALL"]
        data_dict["F_Value"] = variance_data["F"]
        data_dict["P_Value"] = variance_data["P"]
        if variance_data["P"] < 0.05:
            if variance_data["P"] >= 0.01:
                data_dict["F_P_Value"] = "%.2f*" % variance_data["F"]
            else:
                if variance_data["P"] >= 0.001:
                    data_dict["F_P_Value"] = "%.2f**" % variance_data["F"]
                else:
                    data_dict["F_P_Value"] = "%.2f***" % variance_data["F"]

        else:
            data_dict["F_P_Value"] = "%.2f" % variance_data["F"]

        if len(mid_li) > 1:

            mid_quart_data = my_4_quartiles(mid_li)
            data_dict["midValue"] = mid_quart_data[1]
            data_dict["25%"] = mid_quart_data[0]
            data_dict["75%"] = mid_quart_data[2]
        else:
            data_dict["midValue"] = 0
            data_dict["25%"] = 0
            data_dict["75%"] = 0


        data_li.append(data_dict)

    # except Exception as e:
    #     app.logger.error(e)
    #     status = 5000


    if status == 2000:
        return jsonify(data_li)
    else:
        return jsonify(result(status=status, value=""))


# 列联表分析
@app.route('/v1/series_table/<string:UserID>:<string:ProjID>:<string:QuesID>:<string:ColumnID>:<string:ColumnName>:<ColumnEXID>:<string:ColumnEXName>:<string:TableName>:<string:Where>', methods=['GET'])
def SeriesTable(UserID, ProjID, QuesID, ColumnID, ColumnName, ColumnEXID, ColumnEXName, TableName, Where):
    try:
        info, data = SeriesTableModel(ProjID, ColumnID, ColumnEXID, TableName, Where)
        li = []
        var_data = variance(ColumnID, ColumnEXID, TableName, Where)
        chisquare_data = chisquare2way(ColumnID, ColumnEXID, TableName, Where)
        SeriesSubData = SeriesSubOptModel(ProjID, ColumnID)
        countTotal = 0
        sumTotal = 0
        for i in data:
            countTotal += i["SUMDATA"]
            sumTotal += i["SUMALL"]
        for subdata in data:
            data_dict = dict()
            data_dict["columnEXID"] = ColumnEXID
            data_dict["questionshortEXNM"] = ColumnEXID
            data_dict["columnID"] = ColumnID
            data_dict["questionshortNM"] = ColumnName
            data_dict["optionEXID"] = subdata["optEXID"]
            data_dict["optionEXNM"] = subdata["optionEXNM"]
            data_dict["countTotal"] = countTotal #
            data_dict["countN"] = subdata["SUMDATA"]
            data_dict["sum"] = str(subdata["SUMALL"])
            data_dict["average"] = str(subdata["avgdata"])
            data_dict["stdev"] = str(subdata["STDEVALL"])
            data_dict["sumTotal"] = sumTotal #
            data_dict["score"] = float(subdata["avgdata"]) / 5.0 * 100
            data_dict["F_Value"] = var_data["F"]
            data_dict["FP_Value"] = var_data["P"]
            if var_data["P"] < 0.05:
                if var_data["P"] >= 0.01:
                    data_dict["F_P_Value"] = "%.2f*" % var_data["F"]
                else:
                    if var_data["P"] >= 0.001:
                        data_dict["F_P_Value"] = "%.2f**" % var_data["F"]
                    else:
                        data_dict["F_P_Value"] = "%.2f***" % var_data["F"]
            data_dict["X_Value"] = chisquare_data["chisq"]
            data_dict["XP_Value"] = chisquare_data["p"]
            data_dict["X_P_Value"] = ""
            if chisquare_data["p"] < 0.05:
                if var_data["P"] >= 0.01:
                    data_dict["X_P_Value"] = "%.2f*" % chisquare_data["chisq"]
                else:
                    if chisquare_data["p"] >= 0.001:
                        data_dict["X_P_Value"] = "%.2f**" % chisquare_data["chisq"]
                    else:
                        data_dict["X_P_Value"] = "%.2f***" % chisquare_data["chisq"]

            data_dict["sub_option"] = []
            sub_sum = 0
            for subinfo in info:
                if str(subinfo["optEXID"]) == str(subdata["optEXID"]):
                    sub_sum += subinfo["SUMDATA"]
            # print sub_sum
            ssss = SeriesSubData
            for subinfo in info:
                # 1   1
                # 1   2
                # 1   3
                if str(subinfo["optEXID"]) == str(subdata["optEXID"]):
                    for sub_series in ssss:
                        if str(sub_series["optionID"]) == str(int(subinfo["optID"])):
                            sub_series["optionID"] = subinfo["optEXID"]
                            sub_series["optionNM"] = subinfo["optionEXNM"]
                            sub_series["countN"] = subinfo["SUMDATA"]
                            fff = subinfo["SUMDATA"] / float(sub_sum)
                            # print "%.10f" % fff
                            sub_series["countPER"] = "%.10f" % fff
                            sub_series["flag"] = "1"
            for j in ssss:
                if "flag" in j:
                    subdata_dict = dict()
                    subdata_dict["optionID"] = j["optionID"]
                    subdata_dict["optionNM"] = j["optionNM"]
                    subdata_dict["countN"] = j["countN"]
                    subdata_dict["countPER"] = j["countPER"]
                    data_dict["sub_option"].append(subdata_dict)
                else:
                    subdata_dict = dict()
                    subdata_dict["optionID"] = j["optionID"]
                    subdata_dict["optionNM"] = j["optionNM"]
                    subdata_dict["countN"] = 0
                    subdata_dict["countPER"] = 0
                    data_dict["sub_option"].append(subdata_dict)
            li.append(data_dict)
        status = 2000
    except Exception as e:
        app.logger.error(e)
        status = 5000

    # return jsonify(li)
    if status == 2000:
        return jsonify(li)
    else:
        return jsonify(result(status=status, value=""))











