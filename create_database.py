import pymysql
from db import create_sql

# MySQL连接参数
host = 'localhost'
user = 'root'
password = '152668'
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

connection = pymysql.connect(host=host, user=user, password=password, database=database_name)
try:
    with connection.cursor() as cursor:
        for sql in create_sql:
            cursor.execute(sql)
            print(f"Executed: {sql.split('(')[0].strip()}")
    connection.commit()

except Exception as e:
    print(f"Error: {e}")

finally:
    connection.close()
