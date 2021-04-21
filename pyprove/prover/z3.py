import re
from .prover import Prover
from ..human import numeric

Z3_BINARY = "z3"
Z3_STATIC = "-smt2 -st"

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

# Limit format is: `Tnnn-Mnnn` or a subexpression like `M1000`, where
# `T` is lime limit in seconds,
# `M` is memory limit (in megabytes).

LIMIT_ARGS = {
   "T": lambda x: "-T:%s" % x,
   "M": lambda x: "-memory:%s" % x
}

Z3_OK = ["sat", "unsat"]
Z3_FAILED = ["unknown", "timeout"]

KEYS = [
   "total-time"
]

PAT = re.compile(r":(%s)\s*([0-9.]*)" % "|".join(KEYS), flags=re.MULTILINE)

class Z3(Prover):
   
   def __init__(self, limit="T300", args="", binary=None):
      Prover.__init__(self,
         "z3",
         binary if binary else Z3_BINARY,
         f"{Z3_STATIC} {args}" if args else Z3_STATIC,
         limit,
         LIMIT_ARGS,
         Z3_OK,
         Z3_FAILED)

   def parse(self, output):
      status = output[:output.find("\n")]
      result = {key:numeric(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "total-time" in result:
         result["RUNTIME"] = result["total-time"]
         del result["total-time"]
      return result

