from filter_packets import *
from packet_parser import *
from compute_metrics import *

filter()
parse()
compute()
with open("results.csv","w") as file:
	file.write("Node,Category,Metric,Value\n")
	# compile results and send to csv
	# probably a more elegant way but CBA
	# yes, this is ugly
	line = node_num + ",Size,Requests Sent," + sent_requests + "\n"
	file.write(line)
	line = node_num + ",Size,Requests Received," + received_requests + "\n"
	file.write(line)
	line = node_num + ",Size,Replies Sent," + sent_replies + "\n"
	file.write(line)
	line = node_num + ",Size,Replies Received," + received_replies + "\n"
	file.write(line)
	line = node_num + ",Size,Request Bytes Sent," + sent_request_bytes + "\n"
	file.write(line)
	line = node_num + ",Size,Request Bytes Received," + received_request_bytes + "\n"
	file.write(line)
	line = node_num + ",Size,Request Data Sent," + sent_request_data + "\n"
	file.write(line)
	line = node_num + ",Size,Request Data Received," + received_request_data + "\n"
	file.write(line)
	line = node_num + ",Time,Average RTT (ms)," + avg_rtt + "\n"
	file.write(line)
	line = node_num + ",Time,Request Throughput (kB/sec)," + request_throughput + "\n"
	file.write(line)
	line = node_num + ",Time,Request Goodput (kB/sec)," + request_goodput + "\n"
	file.write(line)
	line = node_num + ",Time,Average Reply Delay (us)," + avg_reply_delay + "\n"
	file.write(line)
	line = node_num + ",Distance,Average Request Hop Count," + avg_hops + "\n"
	file.write(line)