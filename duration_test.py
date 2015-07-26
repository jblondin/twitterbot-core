import unittest
from duration import Duration, DurationError

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
