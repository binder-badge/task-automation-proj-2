import re
from pathlib import Path

def compute(packets,node_ip):
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
	default_ttl = 128 
	results = dict()

	for i in range(len(packets)):
		# if is request
		if packets[i]['icmp_type'] == 8:
			packet_size=int(packets[i]["length"])

			# check if request was received or sent. 
			# src = node = sent, otherwise, received
			if packets[i]['src_ip'] == node_ip:
				# 42 = ethernet + ipv4 + icmp headers
				sent_request_data += packet_size - 42
				sent_request_bytes += packet_size 

				
			else:
				received_request_data += packet_size - 42
				received_request_bytes += packet_size
				
				# if the current packet is a request coming from not node's ip, there is an accomanying reply
				avg_reply_delay += (packets[i+1]["timestamp"]-packets[i]["timestamp"])

				# only calculate hops of requests received. if it was sent, the ttl is set to 128 because it was made by the node and hasn't "travelled" anywhere
				packet_ttl = int(packets[i]['info'].split(",")[2])
				avg_hops = default_ttl - packet_ttl

			request_goodput += packet_size


	request_goodput /= float(packets[len(packets)-1]["timestamp"])
	# avg_reply_delay /= sent_requests

	# note to self ask if requests sent by nodes is used in this or requests both sent or received
	avg_hops /= (sent_requests + received_requests) 

	results.update({"Request Bytes Sent":sent_request_bytes}) # done
	results.update({"Request Bytes Received":received_request_bytes}) # done
	results.update({"Request Data Sent":sent_request_data}) # done
	results.update({"Request Data Received":received_request_data}) # done

	results.update({"Request Goodput (kB/sec)":request_goodput}) # done
	results.update({"Average Reply Delay (us)":avg_reply_delay}) # done?
	
	results.update({"Average Request Hop Count":avg_hops}) 
	#print(str(sent_request_bytes) + " " + str(received_request_bytes))
	#print(str(sent_request_data) + " " + str(received_request_data))
	return results