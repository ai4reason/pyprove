import subprocess


def cmd(f_problem, proto, limit, cvc4binary=None, cvc4args=None):
   """Limit format is: 'Tnnn-Rnnn' or a subexpression:
   + `T` is lime limit in seconds,
   + `R` is resource limit (number of SAT conflicts).
   """
   cvc4binary = cvc4binary if cvc4binary else CVC4_BINARY
   cvc4args = cvc4args if cvc4args else CVC4_STATIC
   limits = {x[0]:x[1:] for x in limit.split("-") if x}
   timeout = TIMEOUT % limit["T"] if (TIMEOUT and "T" in limits) else ""
   try:
      limit = [LIMIT[x](limits[x]) for x in limits]
   except:
      raise Exception("pyprove.cvc4.runner: Unknown CVC4 limit for cvc4.runner (%s)"%limits)
   limit = " ".join(limit)
   cmdargs = f"{timeout}{cvc4binary} {cvc4args} {limit} {proto} {f_problem}"
   return cmdargs
    

def run(f_problem, proto="", limit="", cvc4binary=None, cvc4args=None, f_out=None):
   cmdargs = cmd(f_problem, proto, limit, cvc4binary=cvc4binary, cvc4args=cvc4args)
   if f_out:
      with open(f_out,"w") as out:
         return subprocess.call(cmdargs, shell=True, stdout=out, stderr=subprocess.STDOUT)
   else:
      try:
         return subprocess.check_output(cmdargs, shell=True, stderr=subprocess.STDOUT).decode()
      except subprocess.CalledProcessError as e:
         return e.output.decode()

