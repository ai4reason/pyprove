import os
import json

DEFAULT_NAME = "00RESULTS"
DEFAULT_DIR = os.getenv("PYPROVE_RESULTS", DEFAULT_NAME)

def path(prover, bid, sid, ext="json"):
   d_bid = bid.replace("/","-") 
   d_res = prover.name() + "-" + prover.resources()
   f_out = "%s.%s" % (sid, ext)
   return os.path.join(DEFAULT_DIR, d_bid, d_res, f_out)

def exists(prover, bid, sid, ext="json"):
   return os.path.isfile(path(prover, bid, sid, ext=ext))

def load(prover, bid, sid, ext="json"):
   f_json = path(prover, bid, sid, ext=ext)
   if os.path.isfile(f_json):
      return json.load(open(f_json))
   else:
      return {}

def save(prover, bid, sid, res, ext="json"):
   f_json = path(prover, bid, sid, ext=ext)
   os.makedirs(os.path.dirname(f_json), exist_ok=True)
   json.dump(res, open(f_json,"w"), indent=3)

