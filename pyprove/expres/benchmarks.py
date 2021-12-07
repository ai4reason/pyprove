import os

from .. import eprover, log, bar, human
from . import protos, results
from . import solved as solvedb
import logging

BENCHMARKS_DIR = os.getenv("PYPROVE_BENCHMARKS", ".")
TIMEOUT = 7*24*60*60

logger = logging.getLogger(__name__)

def path(bid, problem=""):
   ret = os.path.join(BENCHMARKS_DIR, bid, problem)
   return ret

def problems(bid):
   probs = os.listdir(path(bid))
   probs = [x for x in probs if os.path.isfile(path(bid, x)) and not x.endswith(".cnf")]
   return probs

def compute(bid, pid, problem, limit, force=False, ebinary=None, eargs=None):
   f_problem = path(bid, problem)
   f_out = results.path(bid, pid, problem, limit)
   if force or not os.path.isfile(f_out) or (os.path.getsize(f_out)==0):
      os.system('mkdir -p "%s"' % os.path.dirname(f_out))
      proto = protos.load(pid)
      out = eprover.runner.run(f_problem, proto, limit, ebinary=ebinary, eargs=eargs)
      eprover.posneg.save(out.strip().split("\n"), f_out)
   return results.load(bid, pid, problem, limit)

def run_compute(job):
   return bar.run(compute, job)

def eval(bid, pids, limit, cores=4, debug=[], ebinary=None, eargs=None, options=[], **others):
   def callback(arg, res, bar):
      if eprover.result.solved(res):
         bar.inc_solved()

   force = "force" in debug
   probs = problems(bid)

   logger.info("+ evaluating %s strategies on %d problems" % (len(pids), len(probs)))
   try:
      eta = human.humantime(len(probs)*len(pids)*int(limit.lstrip("T"))/cores)
   except:
      eta = "unknown"
   logger.debug(log.data("- evaluation parameters:", dict(
      bid=bid, 
      limit=limit, 
      pids=pids, 
      problems=human.humanint(len(probs)),
      tasks=human.humanint(len(probs)*len(pids)),
      eta=eta,
   )))
   
   allres = {}
   fmt = "%%%ds" % max(map(len,pids))
   for (n,pid) in enumerate(pids,start=1):
      args = [(bid,pid,problem,limit,force,ebinary,eargs) for problem in probs]
      name = "(%d/%d)" % (n,len(pids))
      if "headless" not in options:
         if pid.startswith("Enigma+"):
            parts = pid.split("+")
            tail = "+".join([parts[i] for i in [2,3,6]])
         else:
            tail = pid
         progbar = bar.SolvedBar(name, max=len(args), tail=tail) 
      else:
         logger.info("- evaluating %s" % pid)
         progbar = None
         callback = None
      outs = bar.applies(name, run_compute, args, 
               cores=cores, bar=progbar, callback=callback)
      res = {x[0:4]:y for (x,y) in zip(args,outs)}
      solvedb.update(res)
      allres.update(res)
   return allres

def cnf(bid, problem, force):
   f_cnf = path(os.path.join(bid, "cnf"), problem)
   if force or not os.path.isfile(f_cnf):
      f_problem = path(bid, problem)
      open(f_cnf,"wb").write(eprover.runner.cnf(f_problem))

def run_cnf(job):
   return bar.run(cnf, job)

def cnfize(bid, cores=4, force=False, **others):
   os.system('mkdir -p "%s"' % path(bid, "cnf"))
   args = [(bid,p,force) for p in problems(bid)]
   bar.applies("Computing CNFs", run_cnf, args, cores=cores)

def solved(bid, pids, limit, cores=4, force=False):
   res = eval(bid, pids, limit, cores=cores, force=force)
   res = {x:res[x] for x in res if eprover.result.solved(res[x])}
   return res

def get(bid, pids, limit):
   probs = problems(bid)
   rkeys = [(bid,pid,problem,limit) for pid in pids for problem in probs]
   print("Loading %d results ..." % len(rkeys))
   ret = {rkey:results.load(*rkey) for rkey in rkeys if results.exists(*rkey)}
   print("done.")
   return ret

