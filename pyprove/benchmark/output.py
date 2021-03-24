import os

DEFAULT_NAME = "00OUTPUTS"
DEFAULT_DIR = os.getenv("PYPROVE_OUTPUTS", DEFAULT_NAME)

def dir(prover, bid, sid):
   d_bid = bid.replace("/","-") 
   d_res = prover.name() + "-" + prover.resources()
   return os.path.join(DEFAULT_DIR, d_bid, d_res, sid)

def path(prover, bid, sid, problem, options=[], ext="out", **others):
   if "no_outputs" in options:
      return None
   #if "no_archive" in options:
   else:
      f_out = "%s.%s" % (problem, ext)
      f = os.path.join(dir(prover, bid, sid), f_out)
      return f
   #else:
   #   f_tar = dir(prover, bid, sid) 
   #   return f"{f_tar}.tar|{problem}.{ext}"

#def exists(prover, bid, sid, problem, ext="out"):
#   f_out = path(prover, bid, sid, problem, ext=ext)
#   return os.path.isfile(f_out) and (os.path.getsize(f_out) > 0)
#
#def load(prover, bid, sid, problem, ext="out"):
#   return open(path(prover, bid, sid, problem, ext=ext)).read()
#
#def save(prover, bid, sid, problem, output, ext="out"):
#   f_out = path(prover, bid, sid, problem, ext=ext)
#   os.makedirs(os.path.dirname(f_out), exist_ok=True)
#   open(f_out,"w").write(output)

