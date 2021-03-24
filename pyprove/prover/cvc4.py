import re
from .prover import Prover
from ..human import numeric

CVC4_BINARY = "cvc4"
CVC4_STATIC = "-L smt2.6 --no-incremental --no-type-checking --no-interactive --stats"

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

# Limit format is: `Tnnn-Rnnn` or a subexpression like `R1000`, where
# `T` is lime limit in seconds,
# `R` is resource limit (number of SAT conflicts).

LIMIT_ARGS = {
   "T": lambda x: "--tlimit=%s" % (1000*int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

CVC4_OK = ["sat", "unsat"]
CVC4_FAILED = ["unknown", "timeout"]

KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::RewriteStep",
   "resource::PreprocessStep",
   "Instantiate::Instantiations_Total",
   "SharedTermsDatabase::termsCount"
]

PAT = re.compile(r"^(%s), (\S*)" % "|".join(KEYS), flags=re.MULTILINE)

class Cvc4(Prover):
   
   def __init__(self, limit="T300", args="", binary=None):
      Prover.__init__(self,
         "cvc4",
         binary if binary else CVC4_BINARY,
         f"{CVC4_STATIC} {args}" if args else CVC4_STATIC,
         limit,
         LIMIT_ARGS,
         CVC4_OK,
         CVC4_FAILED)

   def parse(self, output):
      status = output[:output.find("\n")]
      if (status not in self.status_all) and ("timeout" in status):
         status = "timeout"
      result = {key:numeric(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "driver::totalTime" in result:
         result["RUNTIME"] = result["driver::totalTime"]
         del result["driver::totalTime"]
      return result

