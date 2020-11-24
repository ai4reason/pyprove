from datetime import datetime
from sys import argv, exc_info
import os, io, sys
import atexit
import traceback
import logging
from . import human

REPORTS_DIR = os.getenv("EXPRES_REPORTS", "./00REPORTS")
ENABLED = True

def disable():
   global ENABLED
   ENABLED = False

def enable():
   global ENABLED
   ENABLED = True

def trace():
   text(traceback.format_exc())

def mapping(m, info=None):
   if info:
      msg(info)
   if m:
      size = max([len(str(x)) for x in m])
      pair = "| %%-%ds = %%s" % size
      text("\n".join([pair % (x,m[x]) for x in sorted(m)]))

def start(intro, config=None, script=""):
   msg(intro, script=script, reset=True)
   if config:
      mapping(config)

def msg(msg, cache=[], script="", timestamp=True, reset=False):
   if not ENABLED:
      return
   now = datetime.now()
   if not cache:
      script = argv[0] if argv and not script else script
      cache.append(now)
      os.system("mkdir -p %s" % REPORTS_DIR)
      cache.append(("%s/%s__%s.log" % (REPORTS_DIR, script.lstrip("./").replace("/","+"), now.strftime("%y-%m-%d__%H:%M:%S"))).replace(" ","_"))
      #atexit.register(terminating, cache)
   elif reset:
      cache[0] = now
   
   msg = ("[%s] %s" % (now-cache[0], msg)) if timestamp else msg
   print(msg)
   if REPORTS_DIR:
      f = open(cache[1],"a")
      f.write(msg+"\n")
      f.flush()
      f.close()

def text(msg0=""):
   msg(msg0, timestamp=False)




def terminating():
   logger = logging.getLogger()
   logger.info("Enigmatic Terminating.\n")
   if "last_traceback" in dir(sys):
      traceback.print_last()

CONSOLE = None

def handler(fd, logger0=None):
   global CONSOLE
   logger0 = logging.getLogger() if not logger0 else logger0
   if CONSOLE and CONSOLE in logger0.handlers:
      logger0.removeHandler(CONSOLE)
   CONSOLE = logging.StreamHandler(io.TextIOWrapper(os.fdopen(fd,"wb")))
   CONSOLE.setLevel(logging.DEBUG)
   CONSOLE.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
   logger0.addHandler(CONSOLE)

def logger(name=None, console_only=False, **others):
   logger0 = logging.getLogger()
   logger0.setLevel(logging.DEBUG)
   
   if not console_only:
      os.system("mkdir -p %s" % REPORTS_DIR)
      script = argv[0] if argv and not name else name
      now = datetime.now()
      f_log = "%s/%s.log" % (REPORTS_DIR, script.lstrip("./").replace("/","+"))
      h = logging.FileHandler(f_log)
      h.setLevel(logging.DEBUG)
      h.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
      logger0.addHandler(h)

   handler(sys.stdout.fileno(), logger0)

   logger0.info("Enigmatic Running.")
   atexit.register(terminating)
   return logging.getLogger(name) if name else logger0

def data(msg=None, m={}): 
   size = max([len(str(x)) for x in m])
   pair = "| %%-%ds = %%s" % size
   prefix = (msg + "\n") if msg else "" 
   tab = ("\n".join([pair % (x,human.format(x,m[x])) for x in sorted(m)]))
   return prefix + tab

def table(msg=None, t=[]):
   def size(i):
      return max([len(str(row[i])) for row in t])
   def conv(x):
      return "%.2f" % x if type(x) is float else x
   t = [list(map(conv, row)) for row in t]
   sizes = [size(i) for i in range(len(t[0]))]
   fmts = ["%%-%ds" % s for s in sizes]
   fmt = " | ".join(fmts)
   fmt = "| " + fmt + " |"
   tab = "\n".join([fmt % tuple(row) for row in t])
   prefix = (msg + "\n") if msg else ""
   return prefix + tab

def lst(msg=None, l=[]):
   prefix = (msg + "\n") if msg else ""
   ls = "\n".join(map(str,l)) 
   return prefix + ls


