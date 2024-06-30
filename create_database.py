import pymysql
import argparse
from db import create_sql


# MySQL连接参数
passroot = argparse.ArgumentParser()
passroot.add_argument('-p', '--password', help='MySQL root password', required=True)
passroot.add_argument('-d', '--database', help='Database name', default='jobseeker')
passroot.add_argument('-u', '--user', help='MySQL user name', default='root')
passroot.add_argument('-h', '--host', help='MySQL host name', default='localhost')
args = passroot.parse_args()

password = args.password
database_name = args.database
user = args.user
host = args.host
# 创建数据库连接
connection = pymysql.connect(host=host, user=user, password=password)

try:
    with connection.cursor() as cursor:
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
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
