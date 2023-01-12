# usage: io-network.py [-h] [-a | -l | -i | -o] [-ip IP] [-ns]

# options:
#  -h, --help       show this help message and exit
#  -a, --all        display all connections
#  -l, --local      display local connections
#  -i, --incoming   display incoming connections
#  -o, --outgoing   display outgoing connections
#  -ip IP, --ip IP  filter by IP address
#  -ns, --nslookup  enable nslookup


import psutil
import socket
from tabulate import tabulate
import pandas as pd
import argparse

def nslookup(ip_address):
    if ip_address:
        try:
            return socket.gethostbyaddr(ip_address)[0]
        except socket.herror:
            return None
    return None

def connection_table():
    connections = []
    columns = ["Source IP", "Source Port", "Source Interface", "", "Destination IP", "Destination Port", "Protocol", "DNS Lookup Result", "Connection State", "PID", "Program", "User"]
    local_ips = [addr.address for iface, addrs in psutil.net_if_addrs().items() for addr in addrs if addr.family == socket.AF_INET]
    for connection in psutil.net_connections(kind='inet'):
        connection_info = []
        if connection.laddr:
            source_ip, source_port = connection.laddr
            connection_info.append(source_ip)
            connection_info.append(source_port)
            connection_info.append(None)
            connection_info.append('')
            if connection.raddr:
                destination_ip, destination_port = connection.raddr
                connection_info.append(destination_ip)
                connection_info.append(destination_port)
                if nslookup_enabled:
                    dns_lookup_result = nslookup(destination_ip)
                    connection_info.append(dns_lookup_result)
                else:
                    connection_info.append(None)
            else:
                connection_info.append(None)
                connection_info.append(None)
                connection_info.append(None)
            connection_info.append(connection.type)
            connection_info.append(connection.status)

            try:
                process = psutil.Process(connection.pid)
                connection_info.append(connection.pid)
                connection_info.append(process.name())
                connection_info.append(process.username())
            except psutil.NoSuchProcess:
                connection_info.append(None)
                connection_info.append(None)
                connection_info.append(None)
            connections.append(connection_info)
    dataframe = pd.DataFrame(connections,columns=columns)
    
    if args.all:
        return dataframe
    elif args.local:
        return dataframe.loc[(dataframe['Source IP'].isin(local_ips)) | (dataframe['Destination IP'].isin(local_ips))]
    elif args.incoming:
        return dataframe.loc[dataframe['Destination IP'].isin(local_ips)]
    elif args.outgoing:
        return dataframe.loc[~dataframe['Source IP'].isin(local_ips)]
    else:
        print("Please specify a valid argument")
        return None

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--all", help="display all connections", action="store_true")
    group.add_argument("-l", "--local", help="display local connections", action="store_true")
    group.add_argument("-i", "--incoming", help="display incoming connections", action="store_true")
    group.add_argument("-o", "--outgoing", help="display outgoing connections", action="store_true")
    parser.add_argument("-ip", "--ip", help="filter by IP address", type=str)
    parser.add_argument("-ns", "--nslookup", help="enable nslookup", action="store_true")
    args = parser.parse_args()

    if args.nslookup:
        nslookup_enabled = True
    else:
        nslookup_enabled = False

    connection_df = connection_table()
    if args.ip and connection_df is not None:
        connection_df = connection_df[(connection_df['Source IP'] == args.ip) | (connection_df['Destination IP'] == args.ip)]
    if connection_df is not None:
        print(tabulate(connection_df, headers='keys', tablefmt='fancy_grid'))
    else:
        parser.print_help()

