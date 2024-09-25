import os
import time
import json
import queue
import pymysql
import coloredlogs
import pymysqlpool
from datetime import datetime

cache = {}
root_path = os.getcwd()
THIRDEYEDB_CNX = None
THIRDEYEDB_CNX_DICT = None
cursor = None
coloredlogs.install()

DateGetter = datetime.now().strftime('%Y-%m-%d')
argStartDate = str(DateGetter)
argEndDate = str(DateGetter)


class DataAccess:

    @staticmethod
    def db_details():
        try:
            global host_ip, port_num, user_name, passwd, db
            with open(root_path + '/config.json', 'r') as f:
                js = json.load(f)
                host_ip = js['Db']['host']
                port_num = js['Db']['port']
                user_name = js['Db']['user']
                passwd = js['Db']['passwd']
                db = js['Db']['db']
        except Exception as ex:
            print("Failed to get db_details {}".format(ex))

    @staticmethod
    def connection_open():
        try:
            print('Initiating connection with database')
            global THIRDEYEDB_CNX, THIRDEYEDB_CNX_DICT
            THIRDEYEDB_CNX = pymysql.connect(host=host_ip, port=port_num, user=user_name, passwd=passwd, db=db,
                                             connect_timeout=30)
            # THIRDEYEDB_CNX_DICT = pymysql.connect(host=host_ip, port=port_num, user=user_name, passwd=passwd, db=db,
            #                                       connect_timeout=30, cursorclass=pymysql.cursors.DictCursor)
        except Exception as ex:
            print('Failed to open connection with database {}'.format(ex))

    @staticmethod
    def connection_open_obj():
        try:
            print('Initiating connection with database')
            db_con_obj = pymysql.connect(host=host_ip, port=port_num, user=user_name, passwd=passwd, db=db,
                                         connect_timeout=30, cursorclass=pymysql.cursors.DictCursor)
            return db_con_obj
        except Exception as ex:
            print('Failed to open connection with database {}'.format(ex))

    @staticmethod
    def connection_pool_open_by_name(cpool_name):
        try:
            return pymysqlpool.ConnectionPool(host=host_ip, port=port_num, user=user_name, passwd=passwd,
                                              db=db, size=5, name=cpool_name)
            # return pymysqlpool.ConnectionPool(host=host_ip, port=port_num, user=user_name, passwd=passwd,
            #                                   db=db, size=5, name=cpool_name,cursorclass=pymysql.cursors.DictCursor)
        except Exception as ex:
            print('Error while establishing DB pooling connection'.format(ex))

    @staticmethod
    def connection_close():
        try:
            print('Starting to close connection with database')
            if THIRDEYEDB_CNX.open:
                THIRDEYEDB_CNX.close()
        except Exception as ex:
            print('Failed to close connection with database {}'.format(ex))

    @staticmethod
    def connection_check():
        try:
            print('Starting to verify connection with database')
            THIRDEYEDB_CNX.ping()
            return True
        except Exception as ex:
            print('Failed to establish connection with database')
            return False

    @staticmethod
    def insert_attendance(cur_date):
        try:
            db_obj = DataAccess.connection_open_obj()
            with db_obj.cursor() as cursor:
                cursor.callproc("insert_attendance", [cur_date])
                db_obj.commit()
        except Exception as ex:
            print('Failed while inserting face detection into database {}'.format(ex))
            # print('Failed while inserting predicted object details into the database {}'.format(ex))
        finally:
            cursor.close()
            db_obj.close()
            # DataAccess.connection_close()

    @staticmethod
    def get_attendance_data_by_date(date):
        try:

            db_obj = DataAccess.connection_open_obj()
            with db_obj.cursor() as cursor:
                cursor.callproc("get_attendance_data_by_date", [date])
                result_data = cursor.fetchone()
            return result_data
        except Exception as e:
            print('Failed while fetching attendance data by date from database {}'.format(e))
        finally:
            cursor.close()

    @staticmethod
    def update_attendance(cur_date,time_data):
        try:
            db_obj = DataAccess.connection_open_obj()
            with db_obj.cursor() as cursor:
                cursor.callproc("update_attendance", [cur_date, time_data])
        except Exception as ex:
            print('Failed while inserting face detection into database {}'.format(ex))
        finally:
            db_obj.commit()
            cursor.close()
            db_obj.close()
