'''
Utility classes for handling colors
'''

import unittest

class RGBError(Exception):
  '''Base class for Color errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class RGB(object):
   '''
   Base RGB class 
   '''

   def __init__(self,string="",red=0,green=0,blue=0):
      '''
      RGB constructor
      '''
      if len(string) > 0:
         self.construct_from_string(string)
      else:
         self.construct_from_rgb(red,green,blue)

   def construct_from_string(self,string):
      # remove spaces
      string = "".join(string.split())
      
      if "," in string:
         self.construct_from_triplet(string)
      else:
         self.construct_from_hexcode(string)

   def construct_from_triplet(self,string):
      # remove parentheses
      string = "".join(string.split("("))
      string = "".join(string.split(")"))

      # split on commas
      colors = string.split(",")

      if len(colors) != 3:
         raise RGBError("Color parse error: invalid triplet format: {0}".format(string))

      self.construct_from_rgb(*[int(c) for c in colors])

   def construct_from_hexcode(self,string):
      # remove hash symbol
      string = "".join(string.split("#"))
      # remove '0x' at beginning
      string = "".join(string.split("0x"))

      if len(string) != 6:
         raise RGBError("Color parse error: invalid hexcode: {0}".format(string))

      rgb_split = [string[0:2],string[2:4],string[4:6]]
      self.construct_from_rgb(*[int(color_str,16) for color_str in rgb_split])

   def validate_color(self,c,name):
      if c < 0 or c > 255:
         raise RGBError("Color parse error: {0} value out of range ({1}). Color values must be "
            "between 0 and 255 (inclusive)".format(name,c))

   def construct_from_rgb(self,red,green,blue):

      self.validate_color(red,"red")
      self.validate_color(green,"green")
      self.validate_color(blue,"blue")

      self._red = red
      self._green = green
      self._blue = blue

   @property
   def red(self):
      return self._red
   
   @property
   def green(self):
      return self._green
   
   @property
   def blue(self):
      return self._blue
   
class TestRGB(unittest.TestCase):
   def test_rgb_from_colors(self):
      c = RGB()
      self.assertEquals(c.red,0)
      self.assertEquals(c.green,0)
      self.assertEquals(c.blue,0)

      c = RGB(red=11,green=22,blue=33)
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      c = RGB(green=22,red=11,blue=33)
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      with self.assertRaises(RGBError):
         RGB(red=256,green=44,blue=55)

   def test_rgb_from_triplet(self):
      c = RGB("11,22,33")
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      c = RGB("(11,22,33)")
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      with self.assertRaises(RGBError):
         RGB("11,22,33,44")

      with self.assertRaises(RGBError):
         RGB("11,22,333")

   def test_rgb_from_hexcode(self):
      c = RGB("#0B1621")
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      c = RGB("0x0B1621")
      self.assertEquals(c.red,11)
      self.assertEquals(c.green,22)
      self.assertEquals(c.blue,33)

      with self.assertRaises(RGBError):
         RGB("#0B162133")

      with self.assertRaises(RGBError):
         RGB("#0B160")         

if __name__ == "__main__":
   # run unit tests
   unittest.main()   

