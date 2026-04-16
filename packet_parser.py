import re
from pathlib import Path

#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!

def parse(input_file):
    """
    Parse filtered ICMP packets from:
    - filtered .txt
    - filtered .pcap
    """
    input_path = Path(input_file)
    suffix = input_path.suffix.lower()

    if suffix == ".txt":
        packets = _parse_txt(input_file)
    elif suffix == ".pcap":
        packets = _parse_pcap(input_file)
    else:
        raise ValueError("Input must be a .txt or .pcap file.")

    print(f"Parsed {len(packets)} packets")
    return packets


def _parse_txt(input_file):
    packets = []

	# don't ask what this does. i found it online and it works.
    pattern = re.compile(
        r"^\s*(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+(ICMP)\s+(\d+)\s+(.*)$"
    )

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = pattern.match(line)
            if not match:
                continue

            info = match.group(7)

			#same as above, found online and it works. extracts id, seq, ttl from the info string
            id_match = re.search(r"id=0x([0-9a-fA-F]+)", info)
            seq_match = re.search(r"seq=(\d+)", info)
            ttl_match = re.search(r"ttl=(\d+)", info)

            packet_type = "request" if "request" in info.lower() else "reply"
			#icmp are either type 8 (request) or type 0 (reply)
            icmp_type = 8 if packet_type == "request" else 0

			#expected output format:
			# {packet_num: 1, timestamp: 0.123456, src_ip: '192.168.1.1', ...}
            packets.append(
                {
                    "packet_num": int(match.group(1)),
                    "timestamp": float(match.group(2)),
                    "src_ip": match.group(3),
                    "dst_ip": match.group(4),
                    "protocol": match.group(5),
                    "length": int(match.group(6)),
                    "info": info,
                    "packet_type": packet_type,
                    "icmp_type": icmp_type,
                    "icmp_id": int(id_match.group(1), 16) if id_match else None,
                    "seq": int(seq_match.group(1)) if seq_match else None,
                    "ttl": int(ttl_match.group(1)) if ttl_match else None,
                }
            )

    return packets


def _parse_pcap(input_file):
    try:
        from scapy.all import rdpcap, IP, ICMP
    except ImportError as exception:
        raise ImportError(
            "Scapy is required for .pcap parsing. Install it with: pip install scapy"
        ) from exception

    parsed_packets = []
    packets = rdpcap(input_file)

    for index, packet in enumerate(packets, start=1):
        if IP not in packet or ICMP not in packet:
            continue

        ip_layer = packet[IP]
        icmp_layer = packet[ICMP]

		#0 = reply, 8 = request
        if icmp_layer.type not in (0, 8):
            continue

        packet_type = "request" if icmp_layer.type == 8 else "reply"

        parsed_packets.append(
            {
                "packet_num": index,
                "timestamp": float(packet.time),
                "src_ip": ip_layer.src,
                "dst_ip": ip_layer.dst,
                "protocol": "ICMP",
                "length": len(packet),
                "info": (
                    f"Echo (ping) {packet_type} "
                    f"id=0x{icmp_layer.id:04x}, "
                    f"seq={icmp_layer.seq}, "
                    f"ttl={ip_layer.ttl}"
                ),
                "packet_type": packet_type,
                "icmp_type": int(icmp_layer.type),
                "icmp_id": int(icmp_layer.id),
                "seq": int(icmp_layer.seq),
                "ttl": int(ip_layer.ttl),
            }
        )

    return parsed_packets


"""in need of testing - run this file directly to test both .txt and .pcap parsing with the provided test files"""
#uncomment this block below
# use test_Node1.pcap for testing, it has 10 packets, 5 requests and 5 replies.       

if __name__ == "__main__":
    # test txt parsing
    packets_txt = parse("test_Node1_filtered.txt")
    print("TXT packets:", len(packets_txt))
    print(packets_txt[:2])
    # print(packets_txt[0]['info'])

    # test pcap parsing
    packets_pcap = parse("test_Node1_filtered.pcap")
    print("PCAP packets:", len(packets_pcap))
    print(packets_pcap[:2])
    # print(packets_pcap[0]['info'])