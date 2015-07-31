
class CommandError(Exception):
  '''Base class for twitterbot command errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class Command(object):
   def run(self):
      '''
      To be overriden
      '''
      pass

class CommandFactory(object):

   # dictionary of commands
   commands={}

   @staticmethod
   def create(command_text,context):
      command_words=command_text.split(" ")
      if len(command_words) == 0:
         raise CommandError("Empty Command")
      command_name=command_words[0]
      command_params=command_words[1:]

      if command_name in CommandFactory.commands:
         return CommandFactory.commands[command_name](command_params,context)

      raise CommandError("Unknown Command: {0}".format(command_name))
