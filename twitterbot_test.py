from twitterbot import TwitterBot
import datetime as dt

class TwitterBotTest(TwitterBot):
   def on_update(self):
      print "Tweeting!"
      self.tweet("UnitTest: TwitterBotTest ({0})".format(str(dt.datetime.utcnow())))
      self._running = False

if __name__ == "__main__":
   bot = TwitterBotTest("unittestbot.oauth")
   bot.run()
