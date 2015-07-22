'''
A common duration utility class.
'''

import re
import unittest

def weeks_to_seconds(weeks):
   return weeks*7*24*60*60
def days_to_seconds(days):
   return days*24*60*60
def hours_to_seconds(hours):
   return hours*60*60
def minutes_to_seconds(minutes):
   return minutes*60
def milliseconds_to_seconds(milliseconds):
   return milliseconds/1.0e3
def microseconds_to_seconds(microseconds):
   return microseconds/1.0e6
def nanoseconds_to_seconds(nanoseconds):
   return nanoseconds/1.0e9

def seconds_to_weeks(seconds):
   return seconds/60.0/60.0/24.0/7.0
def seconds_to_days(seconds):
   return seconds/60.0/60.0/24.0
def seconds_to_hours(seconds):
   return seconds/60.0/60.0
def seconds_to_minutes(seconds):
   return seconds/60.0
def seconds_to_milliseconds(seconds):
   return seconds*1.0e3
def seconds_to_microseconds(seconds):
   return seconds*1.0e6
def seconds_to_nanoseconds(seconds):
   return seconds*1.0e9

class DurationError(Exception):
  '''Base class for Duration errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class Duration(object):
   '''
   Generic duration class.

   Can be created with a variety of string-based formats or specific time units (minutes, seconds, 
   etc.)  The duration is accessed by one of the time unit accessor properties (duration.minutes,
   duration.seconds,etc.).  The properties can also be set (e.g. duration.minutes = 5); note that
   this will overwrite the entire duration object.  Even though there are accessors of multiple
   units (seconds, minutes), a single duration object only maintains a single duration value.  The
   accessors are only a utility to expres that duration in different designations.

   Time units available: "weeks","days","hours","minutes","seconds","milliseconds","microseconds",
   "nanoseconds".

   Note that this class does no special processing for leap time or time zone changes.  I.e. all 
   conversions are as naturally expected: a week is 7 days, a day is 24 hours, an hour is 60 
   minutes, a minute is 60 seconds, a second is 1000 milliseconds, a millisecond is 1000 
   microseconds, and a microsecond is 1000 nanoseconds.  Any handling of time zones, daylight
   savings times, and leap seconds would have to happen outside this class.


   '''

   def __init__(self,string="",**kwargs):
      '''
      Duration constructor takes either a string parameter or a keyword argument denoting a 
      particular duration unit.  If a string is specified, the keyword arguments will be ignored. 
      Any numeric value must be greater than or equal to 0.

      ==String Parameter==

      If using a string parameter, there are two available formats. The first takes a series of 
      numbers followed by one or two characters denoting the duration unit (seconds, minutes, etc.):

         [<# weeks>w][<# days>d][<# hours>h][<# minutes>m][<# seconds>s][<# milliseconds>ms][<# microseconds>us][<# nanoseconds>ns]

      One ore more duration units are allowed. For example, '1m24s543ms' will be a duration of one
      minute, 24 seconds, 543 milliseconds, and 0 microseconds, 0 nanoseconds.

      The second string format is:

         <# hours>:<# minutes>:<# seconds>[.<# milliseconds>.[<# microseconds>.[<# nanoseconds>]]]

      The millseconds, microseconds, and nanoseconds are optional (as denoted by the '[]' brackets).
      Example: 2:45:34.234 denotes a duration of 2 hours, 45 minutes, 34 seconds, and 234 
      milliseconds (0 microseconds / nanoseconds).  This format does not allow specification of
      days / weeks (although you can specify a number of hours greater than 24).

      Generally, you can specify a number for a particular duration that exceends the 'natural'
      limits for that duration unit (i.e. you can say something like "14m61s") without parsing 
      failure ("14m61s" would be parsed the same as "15m1s").

      ==Duration Unit Parameters==

      Instead of using a string parameter, the Duration object can be created with one or more 
      specified duration unit(s).  The valid duration units are: ("weeks","days","hours","minutes",
      "seconds","milliseconds","microseconds","nanoseconds") or their shortened versions: ("w","d",
      "h","m","s","ms","us","ns").
      
      Example: 

         dur = duration.Duration(minutes=32,seconds=23)

      This will create a duration object representing 32 minutes and 23 seconds.

      '''
      if len(string) > 0:
         self.construct_from_string(string)
      else:
         self.construct_from_unit_dict(kwargs)

   def construct_from_string(self,string):
      # remove spaces
      string = "".join(string.split())

      if ":" in string:
         self.construct_from_positional_timefield(string)
      else:
         self.construct_from_designated_timefield(string)

   def construct_from_positional_timefield(self,string):
      unit_dict = {}
      pattern = re.compile(r"(\d+):(\d+):(\d+)(?:\.(\d+)(?:\.(\d+)(?:\.(\d+))?)?)?")
      m = pattern.search(string)

      if not m or len(m.groups()) != 6:
         raise DurationError("Duration parse error: HH:MM:SS.MMM.UUU.NNN timefield invalid: "
            "{0}".format(string))

      h,m,s,ms,us,ns = m.groups()
      if h is None or m is None or s is None:
         raise DurationError("Duration parse error: HH:MM:SS not complete: {0}".format(string))
      def set_if_valid(d,key,strval):
         if strval is not None:
            d[key] = float(strval)
      set_if_valid(unit_dict,"h",h)
      set_if_valid(unit_dict,"m",m)
      set_if_valid(unit_dict,"s",s)
      set_if_valid(unit_dict,"ms",ms)
      set_if_valid(unit_dict,"us",us)
      set_if_valid(unit_dict,"ns",ns)

      self.construct_from_unit_dict(unit_dict)


   def construct_from_designated_timefield(self,string):
      unit_dict = {}
      # add the two-character duration units first (so something ending in 'ms' isn't interpreted
      # as minutes)
      string = self.add_duration_unit_to_args(string,"ms",unit_dict)
      string = self.add_duration_unit_to_args(string,"ns",unit_dict)
      string = self.add_duration_unit_to_args(string,"us",unit_dict)
      string = self.add_duration_unit_to_args(string,"s",unit_dict)
      string = self.add_duration_unit_to_args(string,"m",unit_dict)
      string = self.add_duration_unit_to_args(string,"h",unit_dict)
      string = self.add_duration_unit_to_args(string,"d",unit_dict)
      string = self.add_duration_unit_to_args(string,"w",unit_dict)

      self.construct_from_unit_dict(unit_dict)

   def add_duration_unit_to_args(self,string,duration_unit,unit_dict):
      split_timefield = re.split(r"(\d+"+duration_unit+r")",string)
      if len(split_timefield) > 3:
         raise DurationError("Duration parse error: Multiple '{0}' units found in string: "
            "{1}".format(duration_unit,string))
      if len(split_timefield) == 1:
         # not found
         return string
      prefix, matched_timefield, suffix = split_timefield
      # remove the matched timefield from the string
      string = "".join([prefix,suffix])
      # add the numeric portion of the matched timefield to the duration unit dictionary
      try:
         unit_dict[duration_unit] = float(re.sub(duration_unit,'',matched_timefield))
      except ValueError:
         raise DurationError("Duration parse error: unable to convert to number: "
            "{0}".format(matched_timefield))
      return string

   def construct_from_unit_dict(self,unit_dict):
      self._seconds = 0.0
      for key in unit_dict:
         val = unit_dict[key]
         if val < 0:
            raise DurationError("Duration parse error: negative value in keyword argument: " 
               "{0}".format(key));
         if key not in ['weeks','w','days','d','hours','h','minutes','m','seconds','s', \
               'milliseconds','ms','microseconds','us','nanoseconds','ns']:
            raise DurationError("Duration parse error: unknown duration unit specified: "
               "{0}".format(key))

         if key == 'weeks' or key == 'w':
            self._seconds += weeks_to_seconds(val)
         if key == 'days' or key == 'd':
            self._seconds += days_to_seconds(val)
         if key == 'hours' or key == 'h':
            self._seconds += hours_to_seconds(val)
         if key == 'minutes' or key == 'm':
            self._seconds += minutes_to_seconds(val)
         if key == 'seconds' or key == 's':
            self._seconds += val
         if key == 'milliseconds' or key == 'ms':
            self._seconds += milliseconds_to_seconds(val)
         if key == 'microseconds' or key == 'us':
            self._seconds += microseconds_to_seconds(val)
         if key == 'nanoseconds' or key == 'ns':
            self._seconds += nanoseconds_to_seconds(val)

   @property
   def nanoseconds(self):
      return seconds_to_nanoseconds(self._seconds)
   @nanoseconds.setter
   def nanoseconds(self,nanoseconds):
      self._seconds = nanoseconds_to_seconds(nanoseconds)
   
   @property
   def microseconds(self):
      return seconds_to_microseconds(self._seconds)
   @microseconds.setter
   def microseconds(self,microseconds):
      self._seconds = microseconds_to_secondss(microseconds)
   
   @property
   def milliseconds(self):
      return seconds_to_milliseconds(self._seconds)
   @milliseconds.setter
   def milliseconds(self,milliseconds):
      self._seconds = milliseconds_to_seconds(milliseconds)
   
   @property
   def seconds(self):
      return self._seconds
   @seconds.setter
   def seconds(self,seconds):
      self._seconds = seconds
   
   @property
   def minutes(self):
      return seconds_to_minutes(self._seconds)
   @minutes.setter
   def minutes(self,minutes):
      self._seconds = minutes_to_seconds(minutes)

   @property
   def hours(self):
      return seconds_to_hours(self._seconds)
   @hours.setter
   def hours(self,hours):
      self._seconds = hours_to_seconds(hours)
   
   @property
   def days(self):
      return seconds_to_days(self._seconds)
   @days.setter
   def days(self,days):
      self._seconds = days_to_seconds(days)

   @property
   def weeks(self):
      return seconds_to_weeks(self._seconds)
   @weeks.setter
   def weeks(self,weeks):
      self._seconds = weeks_to_seconds(weeks)

   def __str__(self):
      split_by_unit = ['']*8
      secs = self._seconds

      split_by_unit[0], secs = self.extract_print_string(secs,weeks_to_seconds,"w")
      split_by_unit[1], secs = self.extract_print_string(secs,days_to_seconds,"d")
      split_by_unit[2], secs = self.extract_print_string(secs,hours_to_seconds,"h")
      split_by_unit[3], secs = self.extract_print_string(secs,minutes_to_seconds,"m")
      split_by_unit[4], secs = self.extract_print_string(secs,lambda x: x,"s")
      split_by_unit[5], secs = self.extract_print_string(secs,milliseconds_to_seconds,"ms")
      split_by_unit[6], secs = self.extract_print_string(secs,microseconds_to_seconds,"us")
      split_by_unit[7], secs = self.extract_print_string(secs,nanoseconds_to_seconds,"ns")

      return "".join(split_by_unit)

   def extract_print_string(self,seconds,conversion_func,designation_str):
      if seconds >= conversion_func(1):
         num = int(seconds / conversion_func(1))
         string_rep = "{0}{1}".format(num,designation_str)
         return string_rep, (seconds - conversion_func(num))
      else:
         return '', seconds      

class TestDuration(unittest.TestCase):
   def test_designated_timefield(self):
      # basic test
      duration = Duration("34m23s")
      self.assertEqual(duration.seconds,34*60+23)

      # test a long expression (along with a value greater than 'natural' limit: 12d > a week)
      duration = Duration("2w12d10h43m1s42ms44us458ns")
      self.assertTrue(abs(duration.nanoseconds-(458+44*1e3+42*1e6+1*1e9+43*1e9*60+10*60*60*1e9+
         12*24*60*60*1e9+2*7*24*60*60*1e9))<1.0)

      # test out-of-natural-order
      duration = Duration("23ms4m")
      self.assertEqual(duration.seconds,4*60+23./1e3)

      # should raise an error when two 'ms' exist in string
      with self.assertRaises(DurationError):
         Duration("23ms4s234ms")

   def test_positional_timefield(self):
      # HH:MM:SS test
      duration = Duration("12:34:56")
      self.assertEqual(duration.seconds,12*60*60+34*60+56)

      # HH:MM:SS.mmm test
      duration = Duration("12:34:56.789")
      self.assertEqual(duration.minutes,12*60+34+56./60+789/1.e3/60)

      # HH:MM:SS.mmm.uuu.nnn test
      duration = Duration("12:34:56.789.12.345")
      self.assertTrue(abs(duration.nanoseconds-(12*60*60*1e9+34*60*1e9+56*1e9+789*1e6+12*1e3+\
         345))<1.0)

   def test_unit_args(self):
      '''
      Tests the duration unit paramters, and all the properties
      '''

      # test all
      duration = Duration(weeks=1,days=2,hours=34,minutes=56,seconds=7,milliseconds=89,
         microseconds=123,nanoseconds=456);
      self.assertTrue(abs(duration.nanoseconds-(1*7*24*60*60*1e9+2*24*60*60*1e9+34*60*60*1e9+\
         56*60*1e9+7*1e9+89*1e6+123*1e3+456))<1.0)

      # test weeks param
      duration = Duration(weeks=1)
      self.assertEqual(duration.days,7)

      # test days param
      duration = Duration(days=1)
      self.assertEqual(duration.hours,24)

      # test hours param
      duration = Duration(hours=1)
      self.assertEqual(duration.minutes,60)

      # test minutes param
      duration = Duration(minutes=1)
      self.assertEqual(duration.seconds,60)

      # test seconds param
      duration = Duration(seconds=1)
      self.assertEqual(duration.milliseconds,1e3)

      # test milliseconds param
      duration = Duration(milliseconds=1)
      self.assertEqual(duration.microseconds,1e3)

      # test microseconds param
      duration = Duration(microseconds=1)
      self.assertEqual(duration.nanoseconds,1e3)

      # test nanoseconds param
      duration = Duration(nanoseconds=1)
      self.assertEqual(duration.weeks,1./1e9/60/60/24/7)

      # test negative value
      with self.assertRaises(DurationError):
         Duration(seconds=-1)

if __name__ == "__main__":
   # run unit tests
   unittest.main()   
