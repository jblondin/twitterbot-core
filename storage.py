'''
Utility functions for saving simple objects (consisting of simple data types) to plaintext files,
and reading them back.

Note that the storage methods in this file are horribly insecure and should not be used for any
program running in a priveleged context.

This typically should be used only for simple configuration files and the like.  For anything more
complicated, just use pickle or some other serialization method.
'''
import os.path

class StorageError(Exception):
  '''Base class for storage errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

def load_dict(filename):
   '''
   Loads a file into a dictionary.  The file must be of a format similar to initializing a
   dictionary in Python code:

   {'key1':'value1','key2':'value2'}

   Newlines are stripped out (and thus the data file should avoid using the '\' character to denote
   line continuation).
   '''
   source = ""
   with open(filename,'r') as source_file:
      source = "".join(source_file.readlines())
   return eval(source)

def save_dict(d,filename):
   '''
   Saves a dictionary into a file.  The resulting file with contain (in plaintext), the Python
   dictionary in text form. E.g.,

   {'key1':'value1','key2':'value2'}
   '''
   with open(filename,'w') as dest_file:
      dest_file.write('{')
      for k in d.keys():
         if type(d[k]) is str:
            dest_file.write("'{0}':'{1}',".format(k,d[k]))
         else:
            dest_file.write("'{0}':{1},".format(k,d[k]))
      dest_file.write('}')

class StorageMixin(object):
   '''
   A mixin which adds a 'load' and 'save' method to an object, which will write the object's member
   variables into a file.

   This mixin only works with data types with members where the return value of __str__ can be used
   to construct a new identical object.  This works for primitive data types (e.g. the result of
   printing out an integer can be used to construct/assign a new integer).
   '''

   @classmethod
   def load(ClassObj,filename):
      instance = ClassObj()
      if not os.path.isfile(filename):
         # return empty
         return instance
      instance_dict = load_dict(filename)
      for k in instance_dict:
         if k not in instance.__dict__.keys():
            raise StorageError("Error processing storage file ({0}): member variable name '{1}' "
               "not recognized.".format(filename,k))
         instance.__dict__[k] = instance_dict[k]
      return instance

   def save(self,filename):
      save_dict(self.__dict__,filename)
