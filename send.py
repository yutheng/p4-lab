#!/usr/bin/env python3
import argparse
from scapy.all import IP, UDP, Ether, Packet, ByteField, ShortField, bind_layers, get_if_hwaddr, get_if_list, sendp

class MyTunnel(Packet):
    name = "MyTunnel"
    fields_desc = [
        ByteField("hop_limit", 64),
        ShortField("proto_id", 0x0800),
        ByteField("dst_id", 0)
    ]

bind_layers(Ether, MyTunnel, type=0x1212)
bind_layers(MyTunnel, IP, proto_id=0x0800)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ip")
    ap.add_argument("message")
    ap.add_argument("--tunnel", type=int, metavar="N", help="tunnel exit to deliver to")
    ap.add_argument("--hops", type=int, default=64, help="initial tunnel hop limit (default: 64)")
    args = ap.parse_args()

    iface = next(i for i in get_if_list() if i.endswith("-eth0"))
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")
    if args.tunnel is not None:
        pkt = pkt / MyTunnel(hop_limit=args.hops, dst_id=args.tunnel)
    pkt = pkt / IP(dst=args.ip) / UDP(sport=4321, dport=4321) / args.message
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
    print(f"Sent from {iface}.")

if __name__ == "__main__":
    main()