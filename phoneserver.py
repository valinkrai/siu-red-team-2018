import socket
import threading
import random
import configparser
config_file = "phoneserver.ini"
config = configparser.ConfigParser()
config.read(config_file)

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print('Listening on {}:{}'.format(bind_ip, bind_port))




while True:
    client_sock, address = server.accept()
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock, address, config, config_file)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.start()

def handle_client_connection(client_socket, address, config):
    
    request = client_socket.recv(1024)
    print('Received {}'.format(request))
    c_hostname = "undefined"
    c_ip = address
    c_date = "1970-01-01_00:00"
    try:
        (c_team_number, c_hostname, c_date) = str(request).split(',')
        config[c_hostname]
        old_version = int(config[c_hostname]['script']['version'])
        config_file = "phoneserver.{}.ini".format(c_hostname)
        config[c_hostname].read(config_file)
        new_version = int(config[c_hostname]['script']['version'])
        if new_version > old_version:
            # Clear runlist for hostname
            to_be_run[c_hostname] = dict.fromkeys(run_list[c_hostname], True)
        if to_be_run[c_hostname][c_team_number]:
            # Attack logic here
        script = get_script()
        log_string = "Team={} IP={} Hostname={} Password={} Timestamp={}".format(c_team_number, c_ip, c_hostname, password, c_date)
        create_record(log_string)
        
        client_socket.send(password.encode('utf8'))
    except Exception as e:
        print(e)
        client_socket.send("Rood".encode('utf8'))
        print("Invalid connection")
    
    client_socket.close()

def create_record(log_string):
    log_file_name = "encrypted.log"
    with open(log_file_name, "a") as log:
        print(log_string)
        log.write(log_string)