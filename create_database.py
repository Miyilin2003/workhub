import pymysql

# MySQL连接参数
host = 'localhost'
user = 'root'
password = '040428'
database_name = 'jobseeking'

# 创建数据库连接
connection = pymysql.connect(host=host, user=user, password=password)

try:
    with connection.cursor() as cursor:
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created or already exists.")
finally:
    connection.close()
