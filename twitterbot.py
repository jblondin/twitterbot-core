import twitter
import duration
import time
import storage

class TwitterBotError(Exception):
  '''Base class for twitterbot errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class LastIds(storage.StorageMixin):
   '''
   Storage object for the IDs of the last tweets seen on various feeds
   '''
   def __init__(self):
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
                last_id_file="last_ids.dat",
                **kwargs):
      '''
      The twitter bot constructor takes ...(TODO)
      '''
      if len(oauth_config_file) > 0:
         oauth_config = storage.load_data(oauth_config_file)

      # twitter API object
      self._api = twitter.Api(**oauth_config)
      # the user for this bot
      self._me = self._api.VerifyCredentials()
      # duration between checking feed, timeline, replies, etc.
      self._check_period=check_period
      # filename to store last IDs
      self._last_id_filename=last_id_file
      # timelines to watch, and the number of statuses from the timeline to view.  If the count is
      # set to '0', the default number of timelines will be returned.  This can be overwritten in
      # a subclass to watch additional timelines
      self._watched_timelines=[(self._me.screen_name,0)]
      # start by trying to process direct messages.  this will be turned to false if DM access is
      # denied, or can be set to false in subclass
      self._process_direct_messages=True
      # whether or not bot should keep running
      self._running=False
      # whether or not to have extra printouts
      self._DEBUG=False

      # any subclass initialization can go in this class to avoid unnecessary constructor chaining
      self.on_subclass_init(**kwargs)

   def on_subclass_init(self,**kwargs):
      # implemented in subclass
      pass

   def run(self):

      self._running = True

      while self._running:

         # trigger automatic hook
         self.on_update_start()

         last_ids = LastIds.load(self._last_id_filename)

         self.process_watched_timelines()
         last_ids.home = self.process_home_timeline(last_ids.home)
         last_ids.replies = self.process_replies(last_ids.replies)
         last_ids.mentions = self.process_mentions(last_ids.mentions)
         if self._process_direct_messages:
            last_ids.dms = self.process_dms(last_ids.dms)

         last_ids.save(self._last_id_filename)

         self.on_update_end()

         if self._running:
            self.sleep()

   def on_update_start(self):
      # implemented in subclass
      pass
   def on_update_end(self):
      # implemented in subclass
      pass

   def process_watched_timelines(self):
      all_statuses = {}
      for screenname,count in self._watched_timelines:
         all_statuses[screenname] = self._api.GetUserTimeline(screen_name=screenname,count=count)
         if self._DEBUG:
            self.print_statuses("Watched Timeline {0}".format(screenname),all_statuses[screenname])

      # trigger hook
      self.on_watched_timelines(all_statuses)

   def on_watched_timelines(self,statuses):
      # implemented in subclass
      pass

   def process_home_timeline(self,last_id):
      statuses = self._api.GetHomeTimeline(since_id=last_id)
      if self._DEBUG:
         self.print_statuses("Home Timeline",statuses)

      # trigger hook
      self.on_home_timeline(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_home_timeline(self,statuses):
      # implemented in subclass
      pass

   def process_replies(self,last_id):
      statuses = self._api.GetReplies(since_id=last_id)
      if self._DEBUG:
         self.print_statuses("Replies",statuses)

      # trigger hook
      self.on_replies(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_replies(self,statuses):
      # implemented in subclass
      pass

   def process_mentions(self,last_id):
      statuses = self._api.GetMentions(since_id=last_id)
      if self._DEBUG:
         self.print_statuses("Mentions",statuses)

      # trigger hook
      self.on_mentions(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_mentions(self,statuses):
      # implemented in subclass
      pass

   def process_dms(self,last_id):
      statuses = []
      try:
         statuses = self._api.GetDirectMessages(since_id=last_id)
      except twitter.error.TwitterError, e:
         error_args = e.args[0]
         # this can happen if the app is not configused to be able to access direct messages.
         # if this is the case, detect the error, display a warning, and stop trying to access those
         # messages
         if len(error_args) > 0 and 'code' in error_args[0] and error_args[0]['code'] == 93:
            print "WARNING: Access to direct messages denied for this user.  Turning off direct " \
               "message processing."
            self._process_direct_messages=False
            statuses = []
         else:
            raise

      if self._DEBUG:
         self.print_statuses("DMs",statuses)

      # trigger hook
      self.on_dms(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_dms(self,statuses):
      # implemented in subclass
      pass

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

   def tweet(self,message):
      '''
      Simple utility function to tweet a message.
      '''
      self._api.PostUpdate(message)
