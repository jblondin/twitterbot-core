import time
import twitter

import timeutils
import duration
import storage
import command

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
                check_period=duration.Duration(seconds=90),
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
      # a subclass to watch additional timelines.  If this list is empty, no timelines will be
      # specifically watched
      self._watched_timelines=[]
      # start by trying to process direct messages.  this will be turned to false if DM access is
      # denied, or can be set to false in subclass
      self._do_process_direct_messages=False
      # whether or not to check replies
      self._do_process_replies=False
      # whether or not to process home timeline
      self._do_process_home_timeline=False
      # whether or not to process mentions (including commands)
      self._do_process_mentions=True
      # whether or not bot should keep running
      self._running=False
      # whether or not to have extra printouts
      self._DEBUG=False

      # list of screen names allowed to send commands
      self._allowed_bosses_filename="allowed_bosses.dat"
      self._allowed_bosses=storage.load_list(self._allowed_bosses_filename)

      # only respond to actions that are newer than this duration
      # this prevents responding to really old stuff if the bot goes down or if last_ids gets
      # deleted
      self._max_actionable_age=duration.Duration(hours=6)

      # any subclass initialization can go in this class to avoid unnecessary constructor chaining
      self.on_subclass_init(**kwargs)

   def on_subclass_init(self,**kwargs):
      # implemented in subclass
      pass

   def add_self_to_watched_timelines(self,count=1):
      '''
      Helper function to add this bot's own user to watched timelines list
      '''
      self._watched_timelines.append((self._me.screen_name,count))

   def run(self):

      self._running = True
      print "Running with user {0}".format(self._me.screen_name)

      while self._running:

         # trigger automatic hook
         self.on_update_start()

         last_ids = LastIds.load(self._last_id_filename)

         self.process_watched_timelines()

         if self._do_process_home_timeline:
            last_ids.home = self.process_home_timeline(last_ids.home)

         if self._do_process_replies:
            last_ids.replies = self.process_replies(last_ids.replies)

         if self._do_process_mentions:
           last_ids.mentions = self.process_mentions(last_ids.mentions)

         if self._do_process_direct_messages:
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
         try:
            all_statuses[screenname] = self._api.GetUserTimeline(screen_name=screenname,count=count)
         except twitter.TwitterError,te:
            print "ERROR: {0}".format(te.message)

         if self._DEBUG:
            self.print_statuses("Watched Timeline {0}".format(screenname),all_statuses[screenname])

      # trigger hook
      self.on_watched_timelines(all_statuses)

   def on_watched_timelines(self,statuses):
      # implemented in subclass
      pass

   def process_home_timeline(self,last_id):
      statuses=[]
      try:
         statuses = self._api.GetHomeTimeline(since_id=last_id)
      except twitter.TwitterError,te:
         print "ERROR: {0}".format(te.message)

      if self._DEBUG:
         self.print_statuses("Home Timeline",statuses)

      # trigger hook
      if self.actionable(statuses):
        self.on_home_timeline(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_home_timeline(self,statuses):
      # implemented in subclass
      pass

   def process_replies(self,last_id):
      statuses=[]
      try:
         statuses = self._api.GetReplies(since_id=last_id)
      except twitter.TwitterError,te:
         print "ERROR: {0}".format(te.message)

      if self._DEBUG:
         self.print_statuses("Replies",statuses)

      # trigger hook
      if self.actionable(statuses):
        self.on_replies(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_replies(self,statuses):
      # implemented in subclass
      pass

   def process_mentions(self,last_id):
      statuses=[]
      try:
         statuses = self._api.GetMentions(since_id=last_id)
      except twitter.TwitterError,te:
         print "ERROR: {0}".format(te.message)

      if self._DEBUG:
         self.print_statuses("Mentions",statuses)

      if self.actionable(statuses):
        # process the commands
        self.process_commands(statuses)

        # trigger hook
        self.on_mentions(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def process_commands(self,mentions):
      # statuses come in most recent -> least recent order...we want to go the opposite direction
      for status in reversed(mentions):
         if status.user.screen_name in self._allowed_bosses:
            # user is valid, it can issue commands

            # create copy for local processing
            status_txt=status.text

            # strip off the @mention part
            status_txt=self.strip_at_symbols(status_txt)
            print "Command: {0}".format(status_txt)
            # check if first name is 'ctl
            if len(status_txt) > 3 and status_txt[:4]=="ctl ":
              # this is a command; strip off the 'ctl'
              status_txt=" ".join(status_txt.split(" ")[1:])

              try:
                 cmnd=command.CommandFactory.create(status_txt,self)
                 response = cmnd.run()
                 if response is not None:
                    self.reply(status,response)
              except command.CommandError, ce:
                 self.reply(status,"Error: {0}".format(ce.message))


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
            self._do_process_direct_messages=False
            statuses = []
         else:
            print "ERROR: {0}".format(e.message)

      if self._DEBUG:
         self.print_statuses("DMs",statuses)

      # trigger hook
      if self.actionable(statuses):
        self.on_dms(statuses)

      return self.extract_id_if_exists(statuses,last_id)

   def on_dms(self,statuses):
      # implemented in subclass
      pass

   def actionable(self,statuses):
      if len(statuses) > 0:
         most_recent_status=statuses[0]
         td=timeutils.time_since(most_recent_status.created_at)
         if td < self._max_actionable_age.timedelta:
            return True

      return False

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

   def strip_at_symbols(self,status_txt):
      # strip off the @mention part
      while len(status_txt) > 0 and status_txt[0]=='@':
         status_txt=" ".join(status_txt.split(" ")[1:])
      return status_txt

   def tweet(self,message):
      '''
      Simple utility function to tweet a message.
      '''
      try:
         self._api.PostUpdate(message)
      except TwitterError,te:
         print "ERROR: {0}".format(te.message)

   def reply(self,in_reply_to,response):
      try:
         self._api.PostUpdate("@{0} {1}".format(in_reply_to.user.screen_name,response),\
            in_reply_to_status_id=in_reply_to.id)
      except TwitterError,te:
         print "ERROR: {0}".format(te.message)

   def tweet_image(self,image_filename,message):
      try:
         self._api.PostMedia(message,image_filename)
      except twitter.TwitterError,te:
        print "ERROR: {0}".format(te.message)

   def tweet_multiple_images(self,image_filenames,message):
      try:
         self._api.PostMultipleMedia(message,image_filenames)
      except twitter.TwitterError,te:
         print "ERROR: {0}".format(te.message)

   def reply_with_image(self,in_reply_to,image_filename,response):
      try:
         self._api.PostMedia("@{0} {1}".format(in_reply_to.user.screen_name,response),\
            image_filename,in_reply_to_status_id=in_reply_to.id)
      except TwitterError,te:
         print "ERROR: {0}".format(te.message)

   def reply_with_multiple_images(self,in_reply_to,image_filenames,response):
      try:
         self._api.PostMedia("@{0} {1}".format(in_reply_to.user.screen_name,response),\
            image_filenames,in_reply_to_status_id=in_reply_to.id)
      except TwitterError,te:
         print "ERROR: {0}".format(te.message)
