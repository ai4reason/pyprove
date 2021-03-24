import re
from .prover import Prover
from ..human import numeric

E_BINARY = "eprover"
E_STATIC = "-p --resources-info --memory-limit=20480 --print-statistics --tstp-format"

LIMIT_ARGS = {
   "T": lambda x: "--soft-cpu-limit=%s --cpu-limit=%s" % (x,int(x)+1),
   "P": lambda x: "--processed-set-limit=%s" % x,
   "C": lambda x: "--processed-clauses-limit=%s" % x,
   "G": lambda x: "--generated-limit=%s" % x
}

E_OK = ['Satisfiable', 'Unsatisfiable', 'Theorem', 'CounterSatisfiable', 'ContradictoryAxioms']
E_FAILED = ['ResourceOut', 'GaveUp']

INCOMPLETE_E_OK = ['Unsatisfiable', 'Theorem']
INCOMPLETE_E_FAILED = ['ResourceOut', 'GaveUp', 'Satisfiable', 'CounterSatisfiable', 'ContradictoryAxioms']

PATS = {
   "RUNTIME":   re.compile(r"^# User time\s*: (\S*) s"),
   "STATUS":    re.compile(r"^# SZS status (\S*)"),
   "PROCESSED": re.compile(r"^# Processed clauses\s*: (\S*)"),
   "GENERATED": re.compile(r"^# Generated clauses\s*: (\S*)"),
   "PROOFLEN":  re.compile(r"^# Proof object total steps\s*: (\S*)"),
   "PRUNED":    re.compile(r"^# Removed by relevancy pruning/SinE\s*: (\S*)")
}

class EProver(Prover):

   def __init__(self, limit="T300", args="-s", binary=None, complete=True):
      Prover.__init__(self,
         "eprover",
         binary if binary else E_BINARY,
         f"{E_STATIC} {args}" if args else E_STATIC,
         limit,
         LIMIT_ARGS,
         E_OK if complete else INCOMPLETE_E_OK,
         E_FAILED if complete else INCOMPLETE_E_FAILED,
         2)

   def parse(self, output):
      result = {}
      result["STATUS"] = "Unknown"
      for line in output.split("\n"):
         line = line.rstrip()
         # search for patterns from PATS
         if (len(line) > 2) and (line[0] == "#" and line[1] == " " ):
            for pat in PATS:
               mo = PATS[pat].search(line)
               if mo:
                  result[pat] = numeric(mo.group(1))
      return result

