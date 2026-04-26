import re
from pathlib import Path

from filter_packets import *
from packet_parser import *
from compute_metrics import *


CAPTURES_DIR = Path(__file__).parent / "Captures"

# (Category, key returned by compute(), cause results.csv format)
METRIC_ROWS = [
	("Size", "Number of Echo Requests sent",     "Requests Sent"),
	("Size", "Number of Echo Requests received", "Requests Received"),
	("Size", "Number of Echo Replies sent",      "Replies Sent"),
	("Size", "Number of Echo Replies received",  "Replies Received"),
	("Size", "Request Bytes Sent",               "Request Bytes Sent"),
	("Size", "Request Bytes Received",           "Request Bytes Received"),
	("Size", "Request Data Sent",                "Request Data Sent"),
	("Size", "Request Data Received",            "Request Data Received"),
	("Time", "Average Ping RTT",                 "Average RTT (ms)"),
	("Time", "Echo Request Throughput",          "Request Throughput (kB/sec)"),
	("Time", "Request Goodput (kB/sec)",         "Request Goodput (kB/sec)"),
	("Time", "Average Reply Delay (us)",         "Average Reply Delay (us)"),
	("Distance", "Average Request Hop Count",    "Average Request Hop Count"),
]

INT_LABELS = {
	"Requests Sent", "Requests Received", "Replies Sent", "Replies Received",
	"Request Bytes Sent", "Request Bytes Received",
	"Request Data Sent", "Request Data Received",
}
ONE_DECIMAL_LABELS = {
	"Request Throughput (kB/sec)",
	"Request Goodput (kB/sec)",
}


def detect_node_ip(packets):
	# the node's own IP appears in every echo packet (as src or dst).
	if not packets:
		return None
	candidates = {packets[0]["src_ip"], packets[0]["dst_ip"]}
	for p in packets[1:]:
		candidates &= {p["src_ip"], p["dst_ip"]}
		if not candidates:
			break
	if len(candidates) == 1:
		return next(iter(candidates))
	# just in case get the most frequent source of echo requests
	counts = {}
	for p in packets:
		if p["icmp_type"] == 8:
			counts[p["src_ip"]] = counts.get(p["src_ip"], 0) + 1
	if not counts:
		return None
	return max(counts, key=lambda ip: counts[ip])


def format_value(label, value):
	if label in INT_LABELS:
		return str(int(value))
	if label in ONE_DECIMAL_LABELS:
		return f"{value:.1f}"
	return f"{value:.2f}"


# main loop iterates over each Node*.txt capture and runs filter, parse, then compute
node_files = sorted(p for p in CAPTURES_DIR.glob("Node*.txt") if not p.stem.endswith("_filtered"))

with open("results.csv", "w") as file:
	file.write("Node,Category,Metric,Value\n")
	# compile results and send to csv
	for node_file in node_files:
		match = re.search(r"Node(\d+)", node_file.stem)
		if not match:
			continue
		node_num = int(match.group(1))

		filtered_path = filter(str(node_file))
		packets = parse(filtered_path)
		node_ip = detect_node_ip(packets)
		print(f"Node {node_num} IP: {node_ip}")

		metrics = compute(packets, node_ip)

		for category, key, label in METRIC_ROWS:
			file.write(f"{node_num},{category},{label},{format_value(label, metrics[key])}\n")

print("Wrote results.csv")