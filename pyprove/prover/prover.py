import subprocess
import time
import os
import tarfile
import io
import gzip

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

TAR_PAT = "|"

class Prover:
   """
   Generic abstract prover interface.  You need to implement at least method
   `parse` in a derived class.  

   Method `parse` should return a dictionary with results.  Its keys might be
   prover-specific but it should contain at least field `STATUS` (and `RUNTIME`
   will most likely be used in the future).  The value of `STATUS` should be a
   prover-specific status, either in the list `self.status_ok` or
   `self.status_failed`.

   Field `self.limit_resource` is a string of format "Xnnn-Ymmm-Zkkk", where
   `X`,`Y`,...  are single characters for different resource limits supported
   by the prover, and `nnn`, `mmm`, ...  are their specific values.  This
   string is translated to specific prover command line arguments using the
   field `self.limit_args` which should be a dictionary with single character
   keys `X`, `Y`, ... The values should be unary functions which translate
   values `nnn`, `mmm, ... to prover-specific command line arguments.
   Character `T` should be used for time limit and it possibly adds `timeout`
   call to limit time resources.  For example, with `self.limit_args`

   `{"T": lambda x: "--time-limit=%s" % x}`

   and `self.limit_resource` set to `T100` you will get argument
   `--time-limit=100` and additionally 

   `timeout --kill-after=1 --foreground 101`.  

   That is, if the prover does not finish by itself after 100 seconds, it will
   be sent SIGTERM after 101 seconds, and if still running, SIGKILL after 102
   seconds.

   You might want to override the method `cmd` which returns the shell command
   to run the prover, if you need more liberty.
   """

   def __init__(self, name, binary, args, limit_resource, limit_args, status_ok, status_failed, timeout_after=1):
      self.prover_name = name
      self.binary = binary
      self.args = args
      self.limit_resource = limit_resource
      self.status_ok = status_ok
      self.status_failed = status_failed
      self.status_all = self.status_ok + self.status_failed
      self.limits(limit_args, timeout_after)

   def cmd(self, problem, strategy, **others):
      cmdargs = f"{self.cmd_timeout}{self.binary} {self.args} {self.cmd_limits} {strategy} {problem}"
      return cmdargs

   def parse(self, output):
      pass

   def name(self):
      return self.prover_name

   def resources(self):
      return self.limit_resource

   def timeout(self):
      return self.time_resource
   
   def solved(self, result):
      ok = ("STATUS" in result) and (result["STATUS"] in self.status_ok)
      return ok

   def error(self, result):
      return ("STATUS" not in result) or (result["STATUS"] not in self.status_all)

   def output(self, problem, strategy, **others):
      cmd = self.cmd(problem, strategy, **others)
      try:
         output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
         output = e.output
      return output

   def prove(self, problem, strategy="", f_out=None, **others):
      start = time.time()
      output = self.output(problem, strategy, **others)
      if f_out:
         self.save(output, f_out)
      result = self.parse(output.decode())
      result["REALTIME"] = time.time() - start
      return result

   def save(self, output, f_out):
      if TAR_PAT in f_out:
         (f_tar, f_name) = f_out.split(TAR_PAT)
         d_tar = os.path.dirname(f_tar)
         if not os.path.isdir(d_tar):
            os.makedirs(d_tar, exist_ok=True)
         archive = tarfile.open(f_tar, "a:")
         tarinfo = tarfile.TarInfo(f_name+".gz")
         output = gzip.compress(output)
         tarinfo.size = len(output)
         archive.addfile(tarinfo, io.BytesIO(output))
         archive.close()
      else:
         os.makedirs(os.path.dirname(f_out), exist_ok=True)
         open(f_out, "wb").write(output)

   def limits(self, limit_args, timeout_after):
      lims = {x[0]:x[1:] for x in self.limit_resource.split("-") if x}
      self.time_resource = int(lims["T"]) if "T" in lims else None
      timeout = TIMEOUT % (self.time_resource+timeout_after) if (TIMEOUT and self.time_resource) else ""
      try:
         args = [limit_args[x](lims[x]) for x in lims]
      except:
         raise Exception("pyprove.prover: Unknown prover limit string ('%s', possible keys are '%s')" % 
               (self.limit_resource, ",".join(limit_args.keys())))
      self.cmd_timeout = timeout
      self.cmd_limits = " ".join(args)

