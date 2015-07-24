'''
Simple imagebot example
'''

from twitterbot import TwitterBot
import timeutils
import datetime as dt

class ImageBot(TwitterBot):

   def on_subclass_init(self,**kwargs):
      self._my_timeline_count=5

   def on_my_timeline(self,statuses):
      if len(statuses)==0:
         # no tweets yet, let's get started!
         print "WARNING: No tweets found for this bot. Proceeding with initial tweet!"
         self.tweet_an_image()
      else:
         most_recent_tweet= statuses[0]
         td = timeutils.time_since(most_recent_tweet.created_at)
         if td > dt.timedelta(hours=6):
            self.tweet_an_image()

   def tweet_an_image(self):
      print "Tweeting an image!"
      pass


if __name__ == "__main__":
   bot = ImageBot("jblondin.oauth")
   bot.run()
