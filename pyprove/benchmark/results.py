import os
import json
import logging

DEFAULT_NAME = "00RESULTS"
DEFAULT_DIR = os.getenv("PYPROVE_RESULTS", DEFAULT_NAME)

logger = logging.getLogger(__name__)

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

def summary(prover, bids, sids, results, ref=None, **others):
   ret = {}
   bids = frozenset(bids)
   
   if ref:
      # problems solved by the reference strategy
      ref = [r for r in results if r[0] in bids and r[1]==ref]
      ref = [r[2] for r in ref if prover.solved(results[r])]
      ref = frozenset(ref)

   for sid in sids:
      problems = [r for r in results if r[0] in bids and r[1]==sid]
      total = len(problems)
      errors = [r for r in problems if prover.error(results[r])]
      if errors:
         logger.warning("There were errors:\n%s" % "\n".join(map(str,errors)))
      errors = len(errors)
      solves = [r for r in problems if prover.solved(results[r])]
      if ref:
         solves = [r[2] for r in solves]
         solves = frozenset(solves)
         plus = len(solves-ref)
         minus = len(ref-solves)
      solves = len(solves)
      
      ret[sid] = [total, errors, solves]
      if ref:
         ret[sid] += [plus, minus]

   return ret

