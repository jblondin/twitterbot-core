from PIL import Image
import array
from imagebot import ImageBot
import duration

class ImageBotTest(ImageBot):
   def generate(self):
      pixels = array.array('B',[255,0,0]*256**2)
      img = Image.frombytes('RGB',(256,256),pixels)
      image_filename="foo.png"
      img.save(image_filename)
      return (image_filename,"A picture!")

if __name__ == "__main__":
   bot = ImageBotTest("unittestbot.oauth",period_between_tweets=duration.Duration(minutes=1))
   bot.run()
