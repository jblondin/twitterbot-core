import twitter
import duration
import time
import os.path

def evalfile(source_filename):
   source = ""
   with open(source_filename,'r') as source_file:
      source = "".join(source_file.readlines())
   return eval(source)

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

def get_last_ids(filename):
   last_ids = LastIds()
   if not os.path.isfile(filename):
      # return empty
      return last_ids
   dat = ""
   with open(filename,'r') as data_source:
      dat = "".join(data_source.readlines())
   last_ids_map = eval(dat)
   for k in last_ids_map:
      if k not in last_ids.__dict__.keys():
         raise TwitterBotError("Error processing last IDs file ({0}): feed name '{1}' not "
            "recognized.".format(filename,k))
      last_ids.__dict__[k] = last_ids_map[k]
   return last_ids

def save_last_ids(last_ids,filename):
   with open(filename,'w') as dest_file:
      dest_file.write('{')
      for k in last_ids.__dict__.keys():
         dest_file.write("'{0}':'{1}',".format(k,last_ids.__dict__[k]))
      dest_file.write('}')

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
         oauth_config = evalfile(oauth_config_file)
      self._api = twitter.Api(**oauth_config)
      # duration between checking feed, timeline, replies, etc.
      self._check_period=check_period
      # filename to store last IDs
      self._last_id_filename=last_id_file



   def run(self):

      running = True

      while running:

         last_ids = get_last_ids(self._last_id_filename)

         last_ids.my_timeline = self.process_my_timeline()
         last_ids.home = self.process_home_timeline()
         last_ids.replies = self.process_replies()
         last_ids.mentions = self.process_mentions()
         last_ids.dms = self.process_dms()

         #TODO: finish last_ids integration
         #save_last_ids(last_ids,filename)

         self.sleep()

   def process_my_timeline(self):
      statuses = self._api.GetUserTimeline(screen_name='jblondin')
      #print [u"{0},{1}--{2}".format(s.id,s.user.screen_name,s.text) for s in statuses]

   def process_home_timeline(self):
      sid = 0
      statuses = self._api.GetHomeTimeline(since_id=sid,count=200)
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
