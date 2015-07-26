from twitterbot import TwitterBot
import datetime as dt

class TwitterBotTest(TwitterBot):
   def on_update(self):
      message = "UnitTest: TwitterBotTest ({0})".format(str(dt.datetime.utcnow()))
      print "Tweeting: {0}".format(message)
      self.tweet(message)
      self._running = False

if __name__ == "__main__":
   bot = TwitterBotTest("unittestbot.oauth")
   bot.run()
