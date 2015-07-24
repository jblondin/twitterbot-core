import datetime as dt
import time
import email.utils as eu

def time_since(timestamp):
   '''
   Parses timestamp of format 'Thu Jul 23 20:44:28 +0000 2015' and provides the time that has
   elapsed since that timestamp.

   Returns a datetime object
   '''
   now = dt.datetime.utcnow()
   ts = dt.datetime.fromtimestamp(time.mktime(eu.parsedate(timestamp)))
   return now-ts
