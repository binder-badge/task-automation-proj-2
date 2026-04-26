def compute(packets, node_ip):
	# init vars
	# data
	sent_requests = 0
	received_requests = 0
	sent_replies = 0
	received_replies = 0

	sent_request_bytes = 0
	received_request_bytes = 0
	sent_request_data = 0
	received_request_data = 0
	# time
	avg_rtt = 0
	num_rtt = 0
	request_throughput = 0
	request_goodput = 0
	avg_reply_delay = 0
	num_reply_delay = 0
	# dist
	avg_hops = 0
	num_hops = 0

	# others/helper vars
	default_ttl = 128
	results = dict()

	# pre-index replies by (src, dst, seq) so we can pair correctly.
	# replies can come back out of order so we cannot just look at packets[i+1].
	received_replies_by_key = {}
	sent_replies_by_key = {}
	for p in packets:
		if p['icmp_type'] == 0:
			key = (p['src_ip'], p['dst_ip'], p['seq'])
			if p['src_ip'] == node_ip:
				sent_replies_by_key[key] = p
			else:
				received_replies_by_key[key] = p

	for i in range(len(packets)):
		# if is request
		if packets[i]['icmp_type'] == 8:
			packet_size = int(packets[i]["length"])

			# check if request was received or sent.
			# src = node = sent, otherwise, received
			if packets[i]['src_ip'] == node_ip:
				sent_requests += 1
				# 42 = ethernet + ipv4 + icmp headers
				sent_request_data += packet_size - 42
				sent_request_bytes += packet_size

				# match the corresponding received reply by (peer_ip, node_ip, seq)
				key = (packets[i]['dst_ip'], packets[i]['src_ip'], packets[i]['seq'])
				reply = received_replies_by_key.get(key)
				if reply is not None and reply["timestamp"] >= packets[i]["timestamp"]:
					avg_rtt += (reply["timestamp"] - packets[i]["timestamp"])
					num_rtt += 1
					# reply ttl tells us hops the request traveled (symmetric paths).
					# +1 because same-network reply ttl == default_ttl => 1 hop by spec.
					avg_hops += (default_ttl - int(reply['ttl'])) + 1
					num_hops += 1

			else:
				received_requests += 1
				received_request_data += packet_size - 42
				received_request_bytes += packet_size

				# match the corresponding sent reply (this node responding)
				key = (packets[i]['dst_ip'], packets[i]['src_ip'], packets[i]['seq'])
				sent_reply = sent_replies_by_key.get(key)
				if sent_reply is not None and sent_reply["timestamp"] >= packets[i]["timestamp"]:
					avg_reply_delay += (sent_reply["timestamp"] - packets[i]["timestamp"])
					num_reply_delay += 1

		# not request, must be reply
		else:

			# check if reply was received or sent.
			# src = node = sent, otherwise, received
			if packets[i]['src_ip'] == node_ip:
				sent_replies += 1

			else:
				received_replies += 1

	# throughput / goodput per spec: divided by sum of all Ping RTTs (in seconds)
	# avg_rtt is currently the sum of RTTs in seconds; we use it BEFORE averaging.
	if avg_rtt > 0:
		request_throughput = sent_request_bytes / 1000 / avg_rtt
		request_goodput = sent_request_data / 1000 / avg_rtt

	# now convert avg_rtt from sum to average and to milliseconds
	if num_rtt > 0:
		avg_rtt = avg_rtt / num_rtt * 1000

	# average reply delay in microseconds
	if num_reply_delay > 0:
		avg_reply_delay = avg_reply_delay / num_reply_delay * 1_000_000

	# average hop count
	if num_hops > 0:
		avg_hops = avg_hops / num_hops

	results.update({"Number of Echo Requests sent": sent_requests}) #done!
	results.update({"Number of Echo Requests received": received_requests}) #done!
	results.update({"Number of Echo Replies sent": sent_replies}) #done!
	results.update({"Number of Echo Replies received": received_replies}) #done!

	results.update({"Request Bytes Sent": sent_request_bytes}) # done
	results.update({"Request Bytes Received": received_request_bytes}) # done
	results.update({"Request Data Sent": sent_request_data}) # done
	results.update({"Request Data Received": received_request_data}) # done

	results.update({"Average Ping RTT": avg_rtt}) #done!
	results.update({"Echo Request Throughput": request_throughput}) #done

	results.update({"Request Goodput (kB/sec)": request_goodput}) # done
	results.update({"Average Reply Delay (us)": avg_reply_delay}) # done

	results.update({"Average Request Hop Count": avg_hops}) # done
	return results