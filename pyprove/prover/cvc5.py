import re
from .prover import Prover
from ..human import numeric

CVC5_BINARY = "cvc5"
CVC5_STATIC = "-L smt2.6 --no-incremental --no-type-checking --no-interactive --stats --stats-expert"

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

# Limit format is: `Tnnn-Rnnn` or a subexpression like `R1000`, where
# `T` is lime limit in seconds,
# `R` is resource limit (number of SAT conflicts).

LIMIT_ARGS = {
   "T": lambda x: "--tlimit=%s" % (1000*int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

CVC5_OK = ["sat", "unsat"]
CVC5_FAILED = ["unknown", "timeout"]

KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::steps::resource",
   #"resource::RewriteStep",
   #"resource::PreprocessStep",
   "Instantiate::Instantiations_Total",
   "SharedTermsDatabase::termsCount",
   "sat::conflicts",
   "sat::decisions",
   "sat::clauses_literals",
   "sat::propagations",
]

PAT = re.compile(r"^(%s) = (.*)$" % "|".join(KEYS), flags=re.MULTILINE)

class Cvc5(Prover):
   
   def __init__(self, limit="T300", args="", binary=None):
      Prover.__init__(self,
         "cvc5",
         binary if binary else CVC5_BINARY,
         f"{CVC5_STATIC} {args}" if args else CVC5_STATIC,
         limit,
         LIMIT_ARGS,
         CVC5_OK,
         CVC5_FAILED)

   def parse(self, output):
      def parseval(val):
         if val.startswith("{") and val.endswith("}"):
            val = val.strip(" {}")
            val = val.split(",")
            val = [x.split(":") for x in val]
            return {x.strip():numeric(y.strip()) for (x,y) in val}
         return numeric(val)
      status = output[:output.find("\n")]
      if (status not in self.status_all) and ("timeout" in status):
         status = "timeout"
      result = {key:parseval(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "driver::totalTime" in result:
         result["RUNTIME"] = result["driver::totalTime"]
         del result["driver::totalTime"]
      return result

