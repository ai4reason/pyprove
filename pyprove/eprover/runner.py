import subprocess
import os
from subprocess import STDOUT

#PERF = "perf stat -e task-clock:up,page-faults:up,instructions:u"
PERF = ""
TIMEOUT = "timeout --kill-after=%s --foreground %s"
#TIMEOUT = "" # note: never tested with both PERF and TIMEOUT, might work but..

E_BIN = "eprover"
E_ARGS = "%s -p --resources-info --memory-limit=20480 --print-statistics --tstp-format"
E_DEFAULTS = "-s"

LIMIT = {
   "T": lambda x: "--soft-cpu-limit=%s --cpu-limit=%s" % (x,int(x)+1),
   "P": lambda x: "--processed-set-limit=%s" % x,
   "C": lambda x: "--processed-clauses-limit=%s" % x,
   "G": lambda x: "--generated-limit=%s" % x
}

#E_ARGS = "%s -s -p --free-numbers --resources-info --memory-limit=1024 --print-statistics --tstp-format --training-examples=3"
#E_ARGS = "--cpu-limit=%s -s -p --free-numbers --resources-info --memory-limit=1024 --print-statistics --tstp-format --training-examples=3"

def cmd(f_problem, proto, limit, ebinary=None, eargs=None):
   "Limit format is: 'Tnnn-Pnnn-Cnnn-Gnnn' or a subexpression, even like 'Tnnn'."
   ebinary = ebinary if ebinary else E_BIN
   eargs = eargs if eargs else E_DEFAULTS

   limit = "T%s" % limit if isinstance(limit,int) else limit
   limits = {x[0]:x[1:] for x in limit.split("-")}
   if TIMEOUT and "T" in limits:
      # Implement additional external timeout when eprover gets stucked or blocked somewhere.
      # When "Tn" limit is specified then
      # 1) n is passed to eprover as --soft-cpu-limit
      # 2) n+1 is passed to eprover as --cpu-limit
      # 3) if still running after n+5 seconds, timeout system command sends SIGTERM
      # 4) if still running after n+10, timeout sends SIGKILL
      lim_t = int(limits["T"])
      timeout = TIMEOUT % (lim_t+10, lim_t+5)
   else:
      timeout = ""
   try:
      limit = [LIMIT[x](limits[x]) for x in limits]
   except:
      raise Exception("pyprove.eprover.runner: Unknown E limit for eprover.runner (%s)"%limits)
   limit = " ".join(limit)

   estatic = E_ARGS % "%s %s" % (limit, eargs)
   return "%s %s %s %s %s %s" % (PERF,timeout,ebinary,estatic,proto,f_problem)

def run(f_problem, proto, limit, f_out=None, ebinary=None, eargs=None):
   cmd0 = cmd(f_problem, proto, limit, ebinary=ebinary, eargs=eargs)
   env0 = dict(os.environ)
   env0["OMP_NUM_THREADS"] = "1"
   env0["CUDA_VISIBLE_DEVICES"] = "-1"

   if f_out:
      with open(f_out,"w") as out:
         return subprocess.call(cmd0, shell=True, stdout=out, stderr=STDOUT, env=env0)
   else:
      try:
         return subprocess.check_output(cmd0, shell=True, stderr=STDOUT, env=env0).decode()
      except subprocess.CalledProcessError as e:
         return e.output.decode()

def cnf(f_problem):
   cmd0 = "%s --tstp-format --free-numbers --cnf %s" % (E_BIN,f_problem)
   return subprocess.check_output(cmd0, shell=True, stderr=STDOUT)

