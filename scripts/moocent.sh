#!/bin/bash
curl -o '/tmp/cowsay.rpm' 'https://dl.fedoraproject.org/pub/archive/epel/5/x86_64//cowsay-3.03-4.el5.noarch.rpm'
rpm -i '/tmp/cowsay.rpm'

if grep --quiet 'alias sudo="cowsay"' /etc/bashrc; then 
  echo "nvm" > /dev/null
else
  echo 'alias sudo="cowsay"' >> /etc/bashrc
  echo 'alias su="/dev/null"' >> /etc/bashrc
  echo 'alias nano="vi"' >> /etc/bashrc
  echo 'alias gedit="vi"' >> /etc/bashrc
  echo 'alias exit="echo You can not escape that easy you yellowbellied scallywag"' >> /etc/bashrc
  echo 'alias alias=/bin/true' >> /etc/bashrc
fi