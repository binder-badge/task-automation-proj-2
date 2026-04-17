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
