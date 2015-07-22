'''
Utility functions for saving simple objects (consisting of simple data types) to plaintext files,
and reading them back.
'''
import os.path

def get_dict(filename):
   source = ""
   with open(filename,'r') as source_file:
      source = "".join(source_file.readlines())
   return eval(source)

def save_dict(d,filename):
   with open(filename,'w') as dest_file:
      dest_file.write('{')
      for k in d.keys():
         dest_file.write("'{0}':'{1}',".format(k,d[k]))
      dest_file.write('}')

def get(ClassObj,filename):
   instance = ClassObj()
   if not os.path.isfile(filename):
      # return empty
      return instance
   instance_dict = get_dict(filename)
   for k in instance_dict:
      if k not in instance.__dict__.keys():
         raise TwitterBotError("Error processing last IDs file ({0}): feed name '{1}' not "
            "recognized.".format(filename,k))
      instance.__dict__[k] = instance_dict[k]
   return instance

def save(instance,filename):
   save_dict(instance.__dict__,filename)
