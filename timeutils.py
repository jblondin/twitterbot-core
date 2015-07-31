import datetime as dt
import time
import email.utils as eu
import os

def time_since_file(timestamp_filename):

   if not os.path.isfile(timestamp_filename):
      # file doesn't exist; assume infinite time
      return dt.timedelta.max

   with open(timestamp_filename,'r') as timestamp_file:
      timestamp="".join(timestamp_file.readlines())
      ts=dt.datetime.fromtimestamp(time.mktime(eu.parsedate(timestamp)))
      return dt.datetime.utcnow()-ts

   return dt.timedelta.max

def save_now_to_file(timestamp_filename):
   with open(timestamp_filename,'w') as timestamp_file:
      timestamp_file.write(eu.formatdate())

def time_since(timestamp):
   '''
   Parses timestamp of format 'Thu Jul 23 20:44:28 +0000 2015' and provides the time that has
   elapsed since that timestamp.

   Returns a datetime object
   '''
   now = dt.datetime.utcnow()
   ts = dt.datetime.fromtimestamp(time.mktime(eu.parsedate(timestamp)))
   return now-ts
