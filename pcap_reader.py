from scapy.all import *
import string
import argparse
import os

def extract_streams(pcap_file, dest_ip=None):
    tcp_streams = defaultdict(list)

    # Read the pcap file
    packets = rdpcap(pcap_file)

    protocols = [TCP, UDP, ICMP]

    # Extract TCP streams
    for packet in packets:
        for proto in protocols:
            if proto in packet:
                try:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    if dest_ip and dst_ip != dest_ip:
                        continue  # Skip packet if destination IP doesn't match

                    src_port = packet[proto].sport
                    dst_port = packet[proto].dport

                    # Creating a unique stream identifier
                    stream_id = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"

                    # Extracting packet data
                    packet_data = bytes(packet[proto].payload)

                    # Appending packet data to the respective stream
                    tcp_streams[stream_id].append(packet_data)
                except:
                    continue
                continue
    return tcp_streams


def has_printable_characters(input_string):
    for char in input_string:
        if char in string.printable:
            return True
    return False


def print_tcp_streams(tcp_streams, output_file=None):
    if output_file:
        with open(output_file, 'w') as file:
            for stream_id, packets in tcp_streams.items():
                file.write(f"Stream: {stream_id}\n")
                for idx, packet_data in enumerate(packets, start=1):
                    try:
                        str_data = bytes.decode(packet_data, encoding='utf-8')

                        if has_printable_characters(str_data):
                            file.write(str_data + "\n")
                    except:
                        continue
                file.write("=" * 40 + "\n")
    else:
        for stream_id, packets in tcp_streams.items():
            print(f"Stream: {stream_id}")
            for idx, packet_data in enumerate(packets, start=1):
                try:
                    str_data = bytes.decode(packet_data, encoding='utf-8')

                    if has_printable_characters(str_data):
                        print(str_data)
                except:
                    continue
            print("=" * 40)


def main():
    parser = argparse.ArgumentParser(description='Extract TCP streams from a pcap file.')
    parser.add_argument('pcap_file', help='Path to the input pcap file')
    parser.add_argument('--dest-ip', help='Destination IP address to filter packets')
    parser.add_argument('--output-file', help='Output file to save the results')

    args = parser.parse_args()

    pcap_file = args.pcap_file
    dest_ip = args.dest_ip
    output_file = args.output_file

    # Extract TCP streams from pcap file, optionally filtered by destination IP
    tcp_streams = extract_streams(pcap_file, dest_ip=dest_ip)

    # Print or save each element of the list based on the output file option
    print_tcp_streams(tcp_streams, output_file=output_file)


if __name__ == "__main__":
    main()