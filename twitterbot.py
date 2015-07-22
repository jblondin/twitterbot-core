import twitter
import duration
import time
import storage

class TwitterBotError(Exception):
  '''Base class for Duration errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class LastIds(object):
   '''
   Storage object for the IDs of the last tweets seen on various feeds
   '''
   def __init__(self):
      self.my_timeline = 0
      self.home = 0
      self.replies = 0
      self.mentions = 0
      self.dms = 0

class TwitterBot(object):
   '''
   The base twitter bot class 
   '''

   def __init__(self,
                oauth_config_file="",
                oauth_config={},
                check_period=duration.Duration(seconds=30),
                last_id_file="last_ids.dat"):
      '''
      The twitter bot constructor takes ...(TODO)
      '''
      if len(oauth_config_file) > 0:
         oauth_config = storage.get_dict(oauth_config_file)
      self._api = twitter.Api(**oauth_config)
      # duration between checking feed, timeline, replies, etc.
      self._check_period=check_period
      # filename to store last IDs
      self._last_id_filename=last_id_file



   def run(self):

      running = True

      while running:

         last_ids = storage.get(LastIds,self._last_id_filename)

         last_ids.my_timeline = self.process_my_timeline()
         last_ids.home = self.process_home_timeline()
         last_ids.replies = self.process_replies()
         last_ids.mentions = self.process_mentions()
         last_ids.dms = self.process_dms()

         #TODO: finish last_ids integration
         #storage.save(last_ids,filename)

         self.sleep()

   def process_my_timeline(self):
      statuses = self._api.GetUserTimeline(screen_name='jblondin')
      #print [u"{0},{1}--{2}".format(s.id,s.user.screen_name,s.text) for s in statuses]

   def process_home_timeline(self):
      sid = 0
      statuses = self._api.GetHomeTimeline(since_id=sid,count=5)
      print [u"{0},{1}--{2}".format(s.id,s.user.screen_name,s.text) for s in statuses]
      print len(statuses),sid

   def process_replies(self):
      statuses = self._api.GetReplies()
      pass

   def process_mentions(self):
      statuses = self._api.GetMentions()
      pass

   def process_dms(self):
      #FIXME: this apparently doesn't work; permission problem?
      #statuses = self._api.GetDirectMessages()
      pass

   def sleep(self):
      # TODO: update this to only sleep remaining amount
      time.sleep(self._check_period.seconds)


if __name__ == "__main__":
   bot = TwitterBot("jblondin.oauth")
   bot.run()
