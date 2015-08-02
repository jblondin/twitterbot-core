'''
Simple imagebot example
'''

from twitterbot import TwitterBot
import timeutils
import duration
import os.path

class ImageBot(TwitterBot):

   def on_subclass_init(self,**kwargs):
      self._period_between_tweets = duration.Duration(hours=1)
      if 'period_between_tweets' in kwargs:
         self._period_between_tweets = kwargs['period_between_tweets']
      self.add_self_to_watched_timelines()

   def on_watched_timelines(self,statuses):
      my_timeline = statuses[self._me.screen_name]
      if len(my_timeline)==0:
         # no tweets yet, let's get started!
         print "WARNING: No tweets found for this bot. Proceeding with initial tweet!"
         self.generate_and_tweet()
      else:
         most_recent_tweet=my_timeline[0]
         td = timeutils.time_since(most_recent_tweet.created_at)
         if td > self._period_between_tweets.timedelta:
            self.generate_and_tweet()

   def generate_and_tweet(self):
      image_filename,message = self.generate()
      if image_filename and os.path.isfile(image_filename):
         self.tweet_image(image_filename,message)

   def generate(self):
      '''
      Generates an image, saves it to a file, and returns the name of the file.

      Implemented in subclass.
      '''
      return (None,None)
