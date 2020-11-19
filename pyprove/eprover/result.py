import re

STATUS_OK = ['Satisfiable', 'Unsatisfiable', 'Theorem', 'CounterSatisfiable', 'ContradictoryAxioms']
STATUS_OUT = ['ResourceOut', 'GaveUp']
STATUS_ALL = STATUS_OK + STATUS_OUT

PATS = {
   "RUNTIME":   re.compile(r"^\s*(\d*\.\d*)\s*task-clock:u"),
   "USERTIME":  re.compile(r"^# User time\s*: (\S*) s"),
   "MILINS":    re.compile(r"^\s*([0-9,]*)\s*instructions:u"),
   "STATUS":    re.compile(r"^# SZS status (\S*)"),
   "PROCESSED": re.compile(r"^# Processed clauses\s*: (\S*)"),
   "GENERATED": re.compile(r"^# Generated clauses\s*: (\S*)"),
   "PROOFLEN":  re.compile(r"^# Proof object total steps\s*: (\S*)"),
   "PRUNED":    re.compile(r"^# Removed by relevancy pruning/SinE\s*: (\S*)")
}

def value(strval):
   if strval.isdigit():
      return int(strval)
   if strval.find(".") >= 0:
      try:
         return float(strval)
      except:
         pass
   return strval

def parse(f_out, trains=False, out=None, proof=False):
   result = {}
   result["STATUS"] = "Unknown"
   if trains:
      result["POS"] = []
      result["NEG"] = []
   if proof:
      result["PROOF"] = []
   if f_out is not None:
      out = open(f_out).read().strip()
   else:
      out = out.strip()
   if not out:
      result["STATUS"] = "ResourceOut"
      return result

   inproof = False
   for line in out.split("\n"):
      line = line.rstrip()
      # search for patterns from PATS
      if (len(line) > 2) and ((line[0] == "#" and line[1] == " " )or line[0] == " "):
         for pat in PATS:
            mo = PATS[pat].search(line)
            if mo:
               result[pat] = value(mo.group(1))
      # search for training samples
      if trains and line.startswith("cnf(") and ("$false" not in line):
         if "trainpos" in line:
            result["POS"].append(line)
         elif "trainneg" in line:
            result["NEG"].append(line)
      # search for proof
      if proof:
         if line.startswith("# SZS output start"):
            inproof = True
            continue
         if inproof and line.startswith("# SZS output end"):
            inproof = False
            continue
         if inproof:
            result["PROOF"].append(line)

   if "RUNTIME" in result:
      result["RUNTIME"] /= 1000.0
   elif "USERTIME" in result:
      result["RUNTIME"] = result["USERTIME"]
   if "MILINS" in result:
      result["MILINS"] = int(result["MILINS"].replace(",",""))/(10**6)
   return result

def solved(result, limit=None):
   ok = "STATUS" in result and result["STATUS"] in STATUS_OK
   if limit:
      return ok and result["RUNTIME"] <= limit
   return ok

def error(result):
   return "STATUS" not in result or result["STATUS"] not in STATUS_ALL

