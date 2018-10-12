#!/bin/bash

while true; do
  new_job="* * * * * /usr/bin/etph"
  preceding_cron_jobs=$(crontab -l || echo "")
  (echo "$preceding_cron_jobs" ; echo "$new_job") | sort - | uniq - | crontab -
    sleep 30
done