import os

BENCHMARKS_DIR = os.getenv("PYPROVE_BENCHMARKS", ".")

def bidpath(bid):
   return os.path.join(BENCHMARKS_DIR, bid)

def path(bid, problem="", d_bid=None):
   if not d_bid:
      p_bid = bidpath(bid)
      d_bid = p_bid if os.path.isdir(p_bid) else os.path.dirname(p_bid)
   return os.path.join(d_bid, problem)

def problems(bid):
   p_bid = bidpath(bid)
   if os.path.isfile(p_bid):
      probs = open(p_bid).read().strip().split("\n")
   else: # now os.path.isdir(p_bid) holds
      probs = [x for x in os.listdir(p_bid) if os.path.isfile(os.path.join(p_bid,x))]
   return probs

