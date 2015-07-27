from PIL import Image
import array
from imagebot import ImageBot
import duration
import datetime as dt
import time
import random

class ImageBotTest(ImageBot):
   def generate(self):
      # generate a 256x256 image of a random color
      random.seed(time.time())
      r = random.randint(0,255)
      g = random.randint(0,255)
      b = random.randint(0,255)
      pixels = array.array('B',[r,g,b]*256**2)
      img = Image.frombytes('RGB',(256,256),pixels)

      image_filename="unittest.png"
      img.save(image_filename)
      message = "UnitTest: ImageBotTest {0},{1},{2} ({3})".format(r,g,b,str(dt.datetime.utcnow()))
      print "Generated image {0}, tweeting with message: {1}".format(image_filename,message)
      return (image_filename,message)

   def on_update_end(self):
      # only run once
      self._running=False

if __name__ == "__main__":
   bot = ImageBotTest("unittestbot.oauth",period_between_tweets=duration.Duration(minutes=1))
   bot.run()
