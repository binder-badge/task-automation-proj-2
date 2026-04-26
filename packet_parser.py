import re
from pathlib import Path

def parse(input_file, use_hex=True):
    """
    Parse filtered ICMP Echo Request/Reply packets from a filtered .txt file.

    By default reads the hex dump under each packet (bonus path); set
    use_hex=False to fall back to the textual summary line.
    """
    input_path = Path(input_file)
    suffix = input_path.suffix.lower()

    if suffix != ".txt":
        raise ValueError("Input must be a .txt file.")

    if use_hex:
        packets = _parse_hex(input_file)
    else:
        packets = _parse_txt(input_file)
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

            # same as above, found online and it works. extracts id, seq, ttl from the info string
            id_match = re.search(r"id=0x([0-9a-fA-F]+)", info)
            seq_match = re.search(r"seq=(\d+)", info)
            ttl_match = re.search(r"ttl=(\d+)", info)

            # info also contains the cross-reference like "(reply in 442)" /
            # "(request in 441)", so match the leading "Echo (ping) ..." token.
            packet_type = "request" if "Echo (ping) request" in info else "reply"
            # icmp are either type 8 (request) or type 0 (reply)
            icmp_type = 8 if packet_type == "request" else 0

            # expected output format:
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


# ---- Hex dump parsing (bonus) -----------------------------------------------

_SUMMARY_HEAD_RE = re.compile(r"^\s*(\d+)\s+([\d\.]+)")
_HEX_OFFSET_RE = re.compile(r"^[0-9a-fA-F]{4}\s")
_HEX_CHARS = set("0123456789abcdefABCDEF")


def _parse_hex(input_file):
    packets = []
    for block in _split_blocks(input_file):
        pkt = _parse_block_hex(block)
        if pkt is not None:
            packets.append(pkt)
    return packets


def _split_blocks(input_file):
    blocks = []
    current = []
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("No.     Time"):
                if current:
                    blocks.append(current)
                current = [line]
            elif current:
                current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _parse_block_hex(block):
    if len(block) < 2:
        return None

    head = _SUMMARY_HEAD_RE.match(block[1])
    if head is None:
        return None
    packet_num = int(head.group(1))
    timestamp = float(head.group(2))

    raw = _collect_hex_bytes(block[2:])
    # need Eth(14) + IPv4(>=20) + ICMP echo header(8) at minimum
    if len(raw) < 42:
        return None

    # Ethernet II: dst MAC (6), src MAC (6), EtherType (2)
    ethertype = (raw[12] << 8) | raw[13]
    if ethertype != 0x0800:  # IPv4 only
        return None

    # IPv4 header
    ihl = raw[14] & 0x0F
    ip_header_len = ihl * 4
    total_length = (raw[16] << 8) | raw[17]
    ttl = raw[22]
    protocol = raw[23]
    if protocol != 1:  # ICMP
        return None
    src_ip = ".".join(str(b) for b in raw[26:30])
    dst_ip = ".".join(str(b) for b in raw[30:34])

    # ICMP echo header sits right after the IP header
    icmp_off = 14 + ip_header_len
    if len(raw) < icmp_off + 8:
        return None
    icmp_type = raw[icmp_off]
    if icmp_type not in (0, 8):
        return None
    icmp_id = (raw[icmp_off + 4] << 8) | raw[icmp_off + 5]
    seq = (raw[icmp_off + 6] << 8) | raw[icmp_off + 7]

    # Frame length = Ethernet header + everything the IP header says it covers.
    length = 14 + total_length

    packet_type = "request" if icmp_type == 8 else "reply"
    info = (
        f"Echo (ping) {packet_type}  "
        f"id=0x{icmp_id:04x}, seq={seq}, ttl={ttl}"
    )

    return {
        "packet_num": packet_num,
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": "ICMP",
        "length": length,
        "info": info,
        "packet_type": packet_type,
        "icmp_type": icmp_type,
        "icmp_id": icmp_id,
        "seq": seq,
        "ttl": ttl,
    }


def _collect_hex_bytes(lines):
    """Pull the byte values out of Wireshark's hex dump rows."""
    raw = bytearray()
    for line in lines:
        if not _HEX_OFFSET_RE.match(line):
            continue
        # split off the offset, then take 2-char hex tokens until we hit ASCII
        tokens = line.split()
        for tok in tokens[1:]:
            if len(tok) == 2 and tok[0] in _HEX_CHARS and tok[1] in _HEX_CHARS:
                raw.append(int(tok, 16))
            else:
                # the ASCII representation column starts here -> stop this row
                break
    return raw