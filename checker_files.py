import glob
from bs4 import BeautifulSoup
import shutil
import os
import configparser
import time
import sys
import psycopg2
import threading
from parser import simplex_parser

SOURCE_FOLDER = "/apps/backend_bof/files/"
BACKUP_FOLDER = "/apps/backend_bof/files_backup/"

try :
	config = configparser.ConfigParser()
	config.read('setting.ini')
	# DATABASE ACCOUNT
	PG_USERNAME = config['DATABASE']['username']
	PG_PASSWORD = config['DATABASE']['password']
	PG_PORTNAME = config['DATABASE']['portname']
	PG_HOSTNAME = config['DATABASE']['hostname']
	PG_DATABASE = config['DATABASE']['database']
except Exception as e :
	print(e)
	sys.exit()

def stu_insert(list_tupple_item):
	try :
		conn = psycopg2.connect(host=PG_HOSTNAME,
		                        port=PG_PORTNAME,
		                        user=PG_USERNAME,
		                        password=PG_PASSWORD,
		                        database=PG_DATABASE)
		cursor = conn.cursor()
		cursor.executemany('INSERT INTO "SANS_STU_MESSAGE" (esn, unixTime, gps, payload) VALUES (%s, %s, %s, %s)', list_tupple_item)
		conn.commit() # <- We MUST commit to reflect the inserted data
		cursor.close()
		conn.close()
	except Exception as e :
		print(e)

def stu_insert_detail(list_tupple_item):
	try :
		conn = psycopg2.connect(host=PG_HOSTNAME,
		                        port=PG_PORTNAME,
		                        user=PG_USERNAME,
		                        password=PG_PASSWORD,
		                        database=PG_DATABASE)
		cursor = conn.cursor()
		cursor.executemany('INSERT INTO public."SANS_STU_MESSAGE_DETAIL"(\
			stu_id, latitude, longitude, msg_type_1, subtype, msg_type_2,\
			message_type, umn, battery, gps_valid, miss_contact_1, miss_contact_2,\
			gps_fail_count, battery_contact_status, motion, fix_confidence, tx_perburst,\
			gps_fault, transmitter_fault, scheduller_fault, min_interval, max_interval,\
			gps_mean_search_time, gps_fail_count_2, transmition_count, accumulate_contact_1,\
			accumulate_contact_2, accumulate_vibration, contact_1_count, contact_2_count) \
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
			%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', list_tupple_item)
		conn.commit() # <- We MUST commit to reflect the inserted data
		cursor.close()
		conn.close()
	except Exception as e :
		print(e)

def stu_update(col, val, stu_id):
	try :
		conn = psycopg2.connect(host=PG_HOSTNAME,
		                        port=PG_PORTNAME,
		                        user=PG_USERNAME,
		                        password=PG_PASSWORD,
		                        database=PG_DATABASE)
		cursor = conn.cursor()
		cursor.execute('UPDATE "SANS_STU_MESSAGE" SET %s=\'%s\' WHERE id=\'%s\'' % (col, val, stu_id))
		conn.commit() # <- We MUST commit to reflect the update data
		cursor.close()
		conn.close()
	except Exception as e :
		print(e)

def get_stu(is_parse=False):
	stu_records = None
	try :
		conn = psycopg2.connect(host=PG_HOSTNAME,
		                        port=PG_PORTNAME,
		                        user=PG_USERNAME,
		                        password=PG_PASSWORD,
		                        database=PG_DATABASE)
		cursor = conn.cursor()
		cursor.execute('SELECT id, esn, unixtime, gps, payload, is_parse, ctime FROM "SANS_STU_MESSAGE" WHERE is_parse = \'%s\'' % (is_parse))
		stu_records = cursor.fetchall() 
		cursor.close()
		conn.close()
	except Exception as e :
		print(e)

	return stu_records

def reader_job():
	while True :
		stu_records = get_stu()
		
		if stu_records is not None :
			if len(stu_records) > 0 :
				
				stu_detail_list = []
				for row in stu_records :
					# set flag col is_parse is True
					parse_data = simplex_parser(row[4],'')
					
					# set item tupple
					stu_item = (
						row[0],
						parse_data['latitude'],
						parse_data['longitude'],
						parse_data['msg_type_1'],
						parse_data['subtype'],
						parse_data['msg_type_2'],
						parse_data['message_type'],
						parse_data['umn'],
						parse_data['battery'],
						parse_data['gps_valid'],
						parse_data['miss_contact_1'],
						parse_data['miss_contact_2'],
						parse_data['gps_fail_count'],
						parse_data['battery_contact_status'],
						parse_data['motion'],
						parse_data['fix_confidence'],
						parse_data['tx_perburst'],
						parse_data['gps_fault'],
						parse_data['transmitter_fault'],
						parse_data['scheduller_fault'],
						parse_data['min_interval'],
						parse_data['max_interval'],
						parse_data['gps_mean_search_time'],
						parse_data['gps_fail_count_2'],
						parse_data['transmition_count'],
						parse_data['accumulate_contact_1'],
						parse_data['accumulate_contact_2'],
						parse_data['accumulate_vibration'],
						parse_data['contact_1_count'],
						parse_data['contact_2_count']
					)
					stu_detail_list.append(stu_item)

					# set flag stu
					stu_update('is_parse', True, row[0])

				# bulk insert detail
				stu_insert_detail(stu_detail_list)
		# respawn
		time.sleep(1)

def stu_job():
	while True :
		try :
			# read file from files folder
			all_xml_files = glob.glob("%s*.xml" % (SOURCE_FOLDER))

			if len(all_xml_files) > 0 :
				for xml_name in all_xml_files : 
					file = open(xml_name,'r')
					basename = os.path.basename(os.path.realpath(xml_name))

					# open file and concat to string
					str_xml =  []
					for line in file: 
						str_xml.append(line.strip())
					stuXML = BeautifulSoup("".join(str_xml), features="xml")

					# get items stuMessages
					stuMsgs = []
					for stuMsg in stuXML.find_all('stuMessage'):
						# esn, unixTime, gps, payload
						stuMsgs.append((stuMsg.esn.string, stuMsg.unixTime.string, stuMsg.gps.string, stuMsg.payload.string))

					# save into database
					stu_insert(stuMsgs)
					# move to backup folder
					shutil.move(xml_name, "%s%s" % (BACKUP_FOLDER,basename))
					print("File %s is moving to %s%s" % (xml_name,BACKUP_FOLDER,basename ))

		except Exception as e :
			print(e)

		# respawn 
		time.sleep(1)
		print("Spawn")

if __name__ == "__main__":
	# Multithreading jobs
    # stu job
    threading.Thread(target=stu_job).start()
    # reader job
    threading.Thread(target=reader_job).start()