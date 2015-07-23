import twitter
import duration
import time
import storage

#TODO: make this a command-line option
_DEBUG = True

class TwitterBotError(Exception):
  '''Base class for Duration errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class LastIds(storage.StorageMixin):
   '''
   Storage object for the IDs of the last tweets seen on various feeds
   '''
   def __init__(self):
      self.my_timeline = None
      self.home = None
      self.replies = None
      self.mentions = None
      self.dms = None

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
         oauth_config = storage.load_dict(oauth_config_file)
      self._api = twitter.Api(**oauth_config)
      # duration between checking feed, timeline, replies, etc.
      self._check_period=check_period
      # filename to store last IDs
      self._last_id_filename=last_id_file



   def run(self):

      running = True

      while running:

         last_ids = LastIds.load(self._last_id_filename)

         last_ids.my_timeline = self.process_my_timeline(last_ids.my_timeline)
         last_ids.home = self.process_home_timeline(last_ids.home)
         last_ids.replies = self.process_replies(last_ids.replies)
         last_ids.mentions = self.process_mentions(last_ids.mentions)
         last_ids.dms = self.process_dms(last_ids.dms)

         last_ids.save(self._last_id_filename)

         self.sleep()

   def process_my_timeline(self,last_id):
      statuses = self._api.GetUserTimeline(screen_name='jblondin',since_id=last_id)
      if _DEBUG:
         self.print_statuses("My Timeline",statuses)
      return self.extract_id_if_exists(statuses,last_id)

   def process_home_timeline(self,last_id):
      statuses = self._api.GetHomeTimeline(since_id=last_id)
      if _DEBUG:
         self.print_statuses("Home Timeline",statuses)
      return self.extract_id_if_exists(statuses,last_id)

   def process_replies(self,last_id):
      statuses = self._api.GetReplies(since_id=last_id)
      if _DEBUG:
         self.print_statuses("Replies",statuses)
      return self.extract_id_if_exists(statuses,last_id)

   def process_mentions(self,last_id):
      statuses = self._api.GetMentions(since_id=last_id)
      if _DEBUG:
         self.print_statuses("Mentions",statuses)
      return self.extract_id_if_exists(statuses,last_id)

   def process_dms(self,last_id):
      #FIXME: this apparently doesn't work; permission problem?
      #statuses = self._api.GetDirectMessages(since_id=last_id)
      return last_id

   def sleep(self):
      # TODO: update this to only sleep remaining amount
      time.sleep(self._check_period.seconds)

   def extract_id_if_exists(self,statuses,default):
      if len(statuses) > 0:
        return statuses[0].id
      else:
        return default

   def print_statuses(self,header,statuses):
      if len(header):
         print "="*20,header,"="*20
      if len(statuses) == 0:
         print "No statuses."
      index = 1
      for s in statuses:
         print u'{0} @{1},{2} -- {3}'.format(index,s.user.screen_name,s.id,s.text)
         index += 1

if __name__ == "__main__":
   bot = TwitterBot("jblondin.oauth")
   bot.run()
