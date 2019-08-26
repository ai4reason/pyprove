import os
import traceback
from multiprocessing import Pool, Manager
from pyprove.bar  import SolvedBar, ProgressBar

from .. import eprover, log
from . import protos, results
from . import solved as solvedb

BENCHMARKS_DIR = os.getenv("ATPY_BENCHMARKS", ".")
TIMEOUT = 7*24*60*60

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
   if force or not os.path.isfile(f_out):
      os.system("mkdir -p %s" % os.path.dirname(f_out))
      proto = protos.load(pid)
      out = eprover.runner.run(f_problem, proto, limit, f_out, ebinary, eargs)
   return results.load(bid, pid, problem, limit)

def runjob(job):
   queue = job[7]
   try:
      res = compute(*job[0:7])
   except:
      res = {}
      print("Error: "+traceback.format_exc())
   queue.put(res)
   return res

def eval(bid, pids, limit, cores=4, force=False, ebinary=None, eargs=None, **others):
   probs = problems(bid)
   log.msg("+ evaluating %s strategies @ %s (%d problems) @ limit %s @ %s cores" % (len(pids), bid, len(probs), limit, cores))
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   allres = {}
   for (n,pid) in enumerate(pids,start=1):
      jobs = [(bid,pid,problem,limit,force,ebinary,eargs,queue) for problem in probs]
      bar = SolvedBar("(%s/%s)"%(n,len(pids)), max=len(jobs))
      bar.start()
      run = pool.map_async(runjob, jobs, chunksize=1)
      todo = len(jobs)
      while todo:
         r = queue.get(TIMEOUT)
         if eprover.result.solved(r):
            bar.inc_solved()
         todo -= 1
         bar.next()
      bar.finish()
      outs = run.get(TIMEOUT)
      res = {x[0:4]:y for (x,y) in zip(jobs,outs)}
      solvedb.update(res)
      allres.update(res)
   pool.close()
   pool.join()
   return allres

def cnf(bid, problem, force, queue):
   try:
      f_cnf = path(bid, "cnf", problem)
      if force or not os.path.isfile(f_cnf):
         open(f_cnf,"wb").write(eprover.runner.cnf(f_problem))
   except:
      pass
   queue.put(problem)

def cnfize(bid, cores=4, force=False, **others):
   probs = problems(bid)
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   todo = len(probs)
   bar = ProgressBar("CNF", todo)
   def run(p):
      return cnf(bid, p, force, queue) 
   pool.map_async(run, probs)
   while todo:
      queue.get(TIMEOUT)
      todo -= 1
      bar.next()
   bar.finish()
   pool.close()
   pool.join()

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

