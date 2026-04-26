from pathlib import Path

def filter(input_file, output_base=None):
    input_path = Path(input_file)

    if input_path.suffix.lower() != ".txt":
        raise ValueError("Input must be a .txt file")

    if output_base is None:
        output_base = str(input_path.with_name(input_path.stem + "_filtered"))

    output_file = output_base + ".txt"

    blocks = _split_into_blocks(input_path)

    filtered_packets = []
    for block in blocks:
        # summary line is the second line in the block
        # only keep ICMP type 8 (echo request) and type 0 (echo reply)
        if len(block) >= 2 and (
            "Echo (ping) request" in block[1] or "Echo (ping) reply" in block[1]
        ):
            filtered_packets.append(block)

    with open(output_file, "w", encoding="utf-8") as f:
        for block in filtered_packets:
            f.writelines(block)

    print("Filtered", len(filtered_packets), "ICMP packets ->", output_file)
    return output_file


def _split_into_blocks(input_path):
    """split capture into per-packet blocks (each starts with 'No.     Time ...')"""
    blocks = []
    current = []
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
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