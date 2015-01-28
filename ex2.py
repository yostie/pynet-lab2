'''
Author: Mike Yost

Version: 1.0

Purpose: Poll router interface stats every SLEEP_INTERVAL for a MAX_RUNTIME then print a line chart of the data

'''

# IMPORT LIBRARIES

import snmp_helper
import pygal
import time

# CONSTANTS

IP = 'X.X.X.X'
SNMP_PORT = XXXX
SNMP_CREDS = {
	'user' : '****',
	'auth_key' : '****',
	'encr_key' : '****'
}
OIDS = {
	'ifDescr_fa4' : '1.3.6.1.2.1.2.2.1.2.5',
	'ifInOctets_fa4' : '1.3.6.1.2.1.2.2.1.10.5',
	'ifInUcastPkts_fa4' : '1.3.6.1.2.1.2.2.1.11.5',
	'ifOutOctets_fa4' : '1.3.6.1.2.1.2.2.1.16.5',
	'ifOutUcastPkts_fa4' : '1.3.6.1.2.1.2.2.1.17.5'
}

SLEEP_INTERVAL = 300
MAX_RUNTIME = 3600

# DEFINE FUNCTIONS

def snmp_poll(dev, user, oid):

	''' 
	PURPOSE: Perform an SNMPv3 poll of a device.
	INPUT: Takes a 'device' object containing IP and SNMP_PORT, 'user' object containing the SNMPv3 credentials, and the 'oid' to be polled.
	OUTPUT: Returns a readable form of the SNMP data.
	'''
	
	snmp_raw = snmp_helper.snmp_get_oid_v3(dev, user, oid)
	
	return snmp_helper.snmp_extract(snmp_raw)

def create_graph(title, labels, in_desc, in_val, out_desc, out_val, filename):

	'''
	PURPOSE: Creates an input/output line chart.
	INPUT: Chart title, Chart X-axis labels, input data description, input, data, output data description, output data, and filename for chart to be created.
	OUTPUT: Returns nothing but does create a chart.
	'''

	print 'Creating graph %s...' % title

	line_chart = pygal.Line()
	line_chart.title = title
	line_chart.x_labels = labels
	line_chart.add(in_desc, in_val)
	line_chart.add(out_desc, out_val)
	line_chart.render_to_file(filename)

def main():

	debug = False

	# INITIALIZE VARIABLES
	
	device = (IP, SNMP_PORT)
	snmp_user = (SNMP_CREDS.get('user'), SNMP_CREDS.get('auth_key'), SNMP_CREDS.get('encr_key'))
	
	current_sleeptime = 0
	
	in_octets = []
	out_octets = []
	in_ucast_pkts = []
	out_ucast_pkts = []
	
	chart_labels = []
	
	while current_sleeptime <= MAX_RUNTIME:
		
		'''
		As long as the current_sleeptime is less than or equal to the MAX_RUNTIME,
		then perform an SNMP poll for interface statistics.
		
		Add the SLEEP_TIME as a chart X-axis label then go to sleep for SLEEP_INTERVAL.
		'''
		
		print "Grabbing interface statistics for interval %s ..." % current_sleeptime
		
		in_octets.append(int(snmp_poll(device, snmp_user, oid=OIDS.get('ifInOctets_fa4'))))
		out_octets.append(int(snmp_poll(device, snmp_user, oid=OIDS.get('ifOutOctets_fa4'))))
		in_ucast_pkts.append(int(snmp_poll(device, snmp_user, oid=OIDS.get('ifInUcastPkts_fa4'))))
		out_ucast_pkts.append(int(snmp_poll(device, snmp_user, oid=OIDS.get('ifOutUcastPkts_fa4'))))

		chart_labels.append(str(current_sleeptime))
		current_sleeptime = current_sleeptime + SLEEP_INTERVAL
		time.sleep(SLEEP_INTERVAL)
	
	# CREATE GRAPHS OF INTERFACE DATA
	
	print "All data has been collected.  Beginning to create graphs of data."
	create_graph('Input/Output Octets', chart_labels, 'InOctets', in_octets, 'OutOctets', out_octets, 'octets.svg')
	create_graph('Input/Output Unicast Packets', chart_labels, 'InPackets', in_ucast_pkts, 'OutPackets', out_ucast_pkts, 'packets.svg')

if __name__ == '__main__':

    main()
