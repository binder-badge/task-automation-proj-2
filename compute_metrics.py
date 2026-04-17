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

	# others/helper vars
	results = dict()

	# done under the assumption that the packets have already been filtered and parsed, leaving only ICMP ping exchange packets. 
	# this means that the first packet is likely to be an echo request coming from the node in question
	node_ip = packets[0]['src_ip']

	print(node_ip)
	for i in range(len(packets)):
		# if is request
		if packet[i]['icmp_type'] == 8:
			if packet[i]['src_ip'] == node_ip:
				# total length header = ipv4 header + packet
				# + 14 because ethernet header itself is 14 bytes (6 for both src and dst macs + 2 for type), thus getting data of whole frame
				sent_request_data += int(packet[i]["length"])
				sent_request_bytes += int(packet[i]["length"]) + 14

				# if the current packet is a request coming from the node's ip, there is an accomanying reply
				avg_reply_delay += (packet[i+1]["timestamp"]-packet[i]["timestamp"])
				
				
			else:
				received_request_data += int(packet[i]["length"])
				received_request_bytes += int(packet[i]["length"]) + 14


	request_goodput /= (packets[len(packets)-1]["timestamp"] - packets[0]["timestamp"])
	avg_reply_delay /= sent_requests

	# note to self ask if requests sent by nodes is used in this or requests both sent or received
	# avg_hops /= (sent_requests + 

	results.update({"Request Bytes Sent":sent_request_bytes})
	results.update({"Request Bytes Received":received_request_bytes})
	results.update({"Request Data Sent":sent_request_data})
	results.update({"Request Data Received":received_request_data})

	results.update({"Request Goodput (kB/sec)":request_goodput})
	results.update({"Average Reply Delay (us)":avg_reply_delay})
	
	results.update({"Average Request Hop Count":avg_hops})
	#print(str(sent_request_bytes) + " " + str(received_request_bytes))
	#print(str(sent_request_data) + " " + str(received_request_data))
	return results