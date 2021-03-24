import os

DEFAULT_NAME = "00SOLVED"
DEFAULT_DIR = os.getenv("PYPROVE_SOLVED", DEFAULT_NAME)

def path(prover, bid, sid):
   d_bid = bid.replace("/","-") 
   d_res = prover.name() + "-" + prover.resources()
   return os.path.join(DEFAULT_DIR, d_bid, d_res, sid)

def save(prover, bid, sid, results):
   f_solved = path(prover, bid, sid)
   os.makedirs(os.path.dirname(f_solved), exist_ok=True)
   problems = [p for p in results if prover.solved(results[p])]
   open(f_solved, "w").write(("\n".join(sorted(problems)))+"\n")

