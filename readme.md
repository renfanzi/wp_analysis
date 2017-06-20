### 项目: 利用Python进行数据分析

### 项目环境: Python2.7.12


### 项目需求

1. 要求利用Python进行数据分析
....
貌似没啥要求,哈哈哈


### 打包命令
zip -r zk_css.zip zk_css/


### 启动服务
nohup python run.py >/dev/null &

### 杀进程
lsof -i:8001 | awk '{print $2}' | sed '1d' | xargs kill -9