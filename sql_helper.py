"""
SQL database helper file
Contains the functions to initialize, create, and close a project's SQL database
"""

import csv
import pymysql


def create_sql_db_from_file(file_path):
    init_sql_db()
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password'
        )
    cur = conn.cursor()

    cur.execute("use FHWA")

    # path = r'C:\Users\ajia\Desktop\18135 HERE Data\Data Source\HERE\readings.csv'
    csv_data = csv.reader(open(file_path, 'rb'))
    next(csv_data)
    for row in csv_data:
        cur.execute("INSERT INTO Ex_Data(TMC, timestamp, speed, AveSpeed, ref, TT, conf, cvalue) VALUES(%s, %s, %s,%s, %s, %s,%s, %s)", row)

    # close the connection to the database.
    cur.close()
    conn.commit()
    conn.close()


def init_sql_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password'
    )

    cur = conn.cursor()
    cur.execute("create database if not exists FHWA")
    cur.execute("use FHWA")
    cur.execute(
        "Create table if not exists Arc_Data " +
        "(TMC varchar(20), timestamp datetime, speed float(4), AveSpeed float(4), ref float(4),TT float(4), conf int(2), cvalue int(3), Type int(1))")
    cur.execute(
        "Create table if not exists Ex_Data " +
        "(TMC varchar(20), timestamp datetime, speed float(4), AveSpeed float(4), ref float(4),TT float(4), conf int(2), cvalue int(3),Type int(1))")
    cur.execute("Create table if not exists DataType (id int(1), Name varchar(10))")
    cur.execute("Create table if not exists Route (id int(1), Name varchar(10),TMC varchar(20))")
    cur.execute("Create table if not exists Settings (TMC_num int(1),Time_Period int(1),holiday int(1),resolution int(2))")
    cur.execute("create table if not exists TMCs (type int(1), tmc varchar(20), roadway varchar(20), direction varchar(10), length float(4))")

    cur.close()
    conn.commit()
    conn.close()


def close_sql_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password'
    )
    cur = conn.cursor()
    cur.execute("use FHWA")
    cur.execute("Insert into Arc_Data select * from Ex_Data")
    cur.execute("TRUNCATE TABLE Ex_Data")

    cur.close()
    conn.commit()
    conn.close()

