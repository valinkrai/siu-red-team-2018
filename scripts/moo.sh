#!/bin/bash
yum install -y cowsay
echo 'alias sudo="cowsay"' >> /etc/bashrc
echo 'alias su="/dev/null"' >> /etc/bashrc
echo 'alias nano="vi"' >> /etc/bashrc
echo 'alias gedit="vi"' >> /etc/bashrc
echo 'alias exit="echo You can not escape that easy you yellowbellied scallywag"' >> /etc/bashrc
echo 'alias alias=/bin/true' >> /etc/bashrc