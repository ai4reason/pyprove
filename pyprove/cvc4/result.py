import re

CVC4_OK = ["sat", "unsat"]
CVC4_FAILED = ["unknown", "timeout"]
CVC4_ALL = CVC4_OK + CVC4_FAILED

KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::RewriteStep",
   "resource::PreprocessStep",
   "Instantiate::Instantiations_Total",
   "SharedTermsDatabase::termsCount"
]

PAT = re.compile(r"^(%s), (\S*)" % "|".join(KEYS), flags=re.MULTILINE)

def value(strval):
   if strval.isdigit():
      return int(strval)
   if strval.find(".") >= 0:
      try:
         return float(strval)
      except:
         pass
   return strval

def parse(out):
   status = out[:out.find("\n")]
   if (status not in CVC4_ALL) and ("timeout" in status):
      status = "timeout"
   result = {key:-1 for key in KEYS}
   result.update({key:value(val) for (key,val) in PAT.findall(out)})
   result["STATUS"] = status
   return result

def solved(result, limit=None):
   ok = ("STATUS" in result) and (result["STATUS"] in CVC4_OK)
   if limit:
      return ok and result["driver::totalTime"] <= limit
   return ok

def error(result):
   return ("STATUS" not in result) or (result["STATUS"] not in CVC4_ALL)

