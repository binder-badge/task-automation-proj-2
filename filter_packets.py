from pathlib import Path

#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!
#pip install scapy 		<-- is required!!!!


from pathlib import Path


def filter(input_file, output_format="pcap", output_base=None):
    input_path = Path(input_file)

    if input_path.suffix.lower() != ".pcap":
        raise ValueError("Input must be a .pcap file")

    if output_format not in ["pcap", "txt"]:
        raise ValueError("output_format must be pcap or txt")

    if output_base is None:
        output_base = input_path.stem + "_filtered"

    from scapy.all import rdpcap, wrpcap, IP, ICMP

    packets = rdpcap(str(input_path))
    filtered_packets = []

    for packet in packets:
        if IP in packet and ICMP in packet:
            if packet[ICMP].type == 0 or packet[ICMP].type == 8:
                filtered_packets.append(packet)

    if output_format == "pcap":
        output_file = output_base + ".pcap"
        wrpcap(output_file, filtered_packets)

    else:
        output_file = output_base + ".txt"

        with open(output_file, "w") as f:
            for i, packet in enumerate(filtered_packets, start=1):
                ip_layer = packet[IP]
                icmp_layer = packet[ICMP]

                if icmp_layer.type == 8:
                    packet_type = "request"
                else:
                    packet_type = "reply"

                line = (
                    f"{i} "
                    f"{float(packet.time):.6f} "
                    f"{ip_layer.src} "
                    f"{ip_layer.dst} "
                    f"ICMP "
                    f"{len(packet)} "
                    f"Echo (ping) {packet_type} "
                    f"id=0x{icmp_layer.id:04x}, "
                    f"seq={icmp_layer.seq}, "
                    f"ttl={ip_layer.ttl}\n"
                )

                f.write(line)

    print("Filtered", len(filtered_packets), "ICMP packets ->", output_file)
    return output_file


"""this is strictly for testing, in final build it should be commented or removed"""
#uncomment block below to test   
# use test_Node1.pcap for testing, it has 10 packets, 5 requests and 5 replies.       

if __name__ == "__main__":
    # Default test -> outputs filtered .pcap
    output_file = filter("test_Node1.pcap")
    print("Created:", output_file)

    # Optional txt test
    txt_file = filter("test_Node1.pcap", output_format="txt")
    print("Created:", txt_file)