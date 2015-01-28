'''
Author: Mike Yost

Version: 1.0

Purpose: Determine whether or not the running configuration has changed during a specific time interval.  If it has, send an alert email.  Check status every 5 minutes.

'''

# IMPORT LIBRARIES

import snmp_helper
import email_helper
import os.path
import time
import pickle

# CONSTANTS

IP = 'X.X.X.X'
SNMP_PORT = XXXX
SNMP_CREDS = {
	'user' : '****',
	'auth_key' : '****',
	'encr_key' : '****'
}
OIDS = {
	'run_last_changed' : '1.3.6.1.4.1.9.9.43.1.1.1.0',
	'start_last_changed' : '1.3.6.1.4.1.9.9.43.1.1.3.0',
	'sysname' : '1.3.6.1.2.1.1.5.0'
}

SLEEP_INTERVAL = 300

# DEFINE FUNCTIONS

def init_run_last_changed():

	if os.path.exists("run_last_changed.pkl"):

		print "Save file exists.  Loading save file...\n"
		file = open("run_last_changed.pkl", "rb")
		file_data = pickle.load(file)
		file.close()
		return int(file_data)

	else:

		print "First time script has been run.  Initializing save file...\n"
		file = open("run_last_changed.pkl", "wb")
		file_data = '0'
		pickle.dump(file_data, file)
		file.close()
		return int(file_data)

def dump_run_last_changed(file_data):
	file = open ("run_last_changed.pkl", "wb")
	pickle.dump(file_data, file)
	file.close()
	return True
		
def check_run_changed(previous_run_change_time, current_run_change_time):
	
	if current_run_change_time > previous_run_change_time:
		return True
	else:
		return False

def send_alert_mail(dev_name, run_last_changed):

	recipient = 'mikey@fltg.com'
	subject = "Running config of %s was changed at %s" % (dev_name, run_last_changed)
	message = '''You better look at this.
'''
	sender = 'pynetlab@twb-tech.com'
	email_helper.send_mail(recipient, subject, message, sender)
	
	return True

def snmp_poll(dev, user, oid):

	snmp_raw = snmp_helper.snmp_get_oid_v3(dev, user, oid)
	
	return snmp_helper.snmp_extract(snmp_raw)

def main():

	debug = False

	device = (IP, SNMP_PORT)
	snmp_user = (SNMP_CREDS.get('user'), SNMP_CREDS.get('auth_key'), SNMP_CREDS.get('encr_key'))
	iterations = 12
	previous_run_last_changed = init_run_last_changed()
	sysname = snmp_poll(device, snmp_user, oid=OIDS.get('sysname'))
	
	if previous_run_last_changed == 0:
		
		print "Polling router for the last time the running config was changed..."
		
		current_run_last_changed = int(snmp_poll(device, snmp_user, oid=OIDS.get('run_last_changed')))
		dump_run_last_changed(current_run_last_changed)
		previous_run_last_changed = current_run_last_changed
		
		if debug is True:
			print "Previous: %s" % previous_run_last_changed
			print "Current: %s" % current_run_last_changed
			print "Iteration: %s\n" % iterations
		
		iterations = iterations - 1	
		time.sleep(SLEEP_INTERVAL)

	while iterations != 0:

		print "Polling router for the last time the running config was changed..."
		
		current_run_last_changed = int(snmp_poll(device, snmp_user, oid=OIDS.get('run_last_changed')))
		dump_run_last_changed(current_run_last_changed)
		run_changed_status = check_run_changed(previous_run_last_changed, current_run_last_changed)
		previous_run_last_changed = current_run_last_changed

		if run_changed_status is True:
		
			print "The running config has changed in this 300 second interval.  Sending email notification."
			send_alert_mail(sysname, current_run_last_changed)

		if debug is True:
			print "Previous: %s" % previous_run_last_changed
			print "Current: %s" % current_run_last_changed
			print "Iteration: %s\n" % iterations
		
		iterations = iterations - 1
		time.sleep(SLEEP_INTERVAL)

	print "The script has finished running."

if __name__ == '__main__':

    main()
