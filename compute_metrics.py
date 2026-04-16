import re
from pathlib import Path

def compute(packets):
	# init vars
	# data
	sent_requests=0
	received_requests=0
	sent_replies=0
	received_replies=0
	sent_request_bytes=0
	received_request_bytes=0
	sent_request_data=0
	received_request_data=0
	# time
	avg_rtt=0
	request_throughput=0
	request_goodput=0
	avg_reply_delay=0
	# dist
	avg_hops=0

	result = dict()
	for packet in packets:
		
		