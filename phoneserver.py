import socket
import threading
import random
import configparser


def main():
    # Load server specific configuration    
    config_file = "phoneserver.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    bind_ip = config['server']['ip']
    bind_port = int(config['server']['port'])

    # Start TCP listener
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)  # max backlog of connections
    
    # Contains dictionary which will hold the configparsers to configure the scripts to server for each host and their version
    host_configs = dict()
    for host_name in config['server']['hosts'].split(','):
        host_configs[host_name] = configparser.ConfigParser()
        host_configs[host_name].read('phoneserver_default.ini')
    ## Sets up the to_be_run dictionary, which tracks which hosts have already received an up to date script
    to_be_run = dict()
    for host_name in config['server']['hosts'].split(','):
        to_be_run[host_name] = dict()
        for team_number in config['server']['teams'].split(','):
            to_be_run[host_name][team_number] = True
        

    print('Listening on {}:{}'.format(bind_ip, bind_port))




    while True:
        client_sock, address = server.accept()
        #print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock, address, config, host_configs, to_be_run,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()

def handle_client_connection(client_socket, address, config, host_configs, to_be_run):
    
    request = client_socket.recv(1024)
    #print('Received {}'.format(request))
    c_hostname = "undefined"
    c_ip = address
    c_date = "1970-01-01_00:00"
    #try:
    (c_team_number, c_hostname, c_date) = str(request.decode('utf-8')).split(',')
    config_file = "phoneserver_{}.ini".format(c_hostname)
    #config[c_hostname]
    old_version = int(host_configs[c_hostname]['script']['version'])
    host_configs[c_hostname].read(config_file)
    new_version = int(host_configs[c_hostname]['script']['version'])
    if new_version > old_version:
        # Clear runlist for hostname
        print("Host {} needs updated New version{}: Old version: {}.".format(c_hostname, new_version, old_version))
        to_be_run[c_hostname][c_team_number] = dict.fromkeys(to_be_run[c_hostname], True)
    if to_be_run[c_hostname][c_team_number]:
        # Attack logic here
        print("to_be_run[{}][{}] is {}".format(c_hostname, c_team_number, to_be_run[c_hostname][c_team_number]))
        script = get_script(host_configs[c_hostname]['script']['file_name'])
        to_be_run[c_hostname][c_team_number] = False
        log_string = "Team={} IP={} Hostname={} Password={} Timestamp={}".format(c_team_number, c_ip, c_hostname, host_configs[c_hostname]['script']['file_name'], c_date)
        create_record(log_string, c_team_number)
        print(script)
        client_socket.send(script.encode('utf-8'))
    else:
        log_string = "Team={} IP={} Hostname={} Action=checkin_no_update Timestamp={}".format(c_team_number, c_ip, c_hostname, c_date)
        create_record(log_string, c_team_number)
        client_socket.send('no'.encode('utf-8'))
    ###
        
    """
    except Exception as e:
        print(str(e))  
        client_socket.send("Error".encode('utf8'))
        print("Invalid connection")
        client_socket.close()
    """
    client_socket.close()

def create_record(log_string, team_number):
    log_file_name = "phone_home_team_{}.log".format(team_number)
    with open(log_file_name, "a") as log:
        print(log_string)
        log.write(log_string)

def get_script(filename):
    try:
        with open(filename, 'r') as file:
            script = file.read()
            return script
    except Exception as e:
        print(e)
        return "#!/bin/bash\n/bin/false"

main()