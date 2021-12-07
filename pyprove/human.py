
def numeric(strval):
   if strval.isdigit():
      return int(strval)
   if strval.count(".") == 1 and strval[-1] != ".":
      return float(strval)
   return strval

def format(key, val):
   #for unit in UNITS:
   #   if unit in key:
   #      return UNITS[unit](val)
   #return str(val)
   unit = key[key.rfind(".")+1:]
   return UNITS[unit](val) if unit in UNITS else str(val)

def humanbytes(b):
   units = {0 : 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB'}
   power = 1024
   n = 0
   while b > power:
      b /= power
      n += 1
   return "%.2f %s" % (b, units[n])

def humanint(n):
   s = str(int(abs(n)))
   r = s[-3:]
   s = s[:-3]
   while s:
      r = s[-3:] + "," + r
      s = s[:-3]
   return r if n >= 0 else "-%s" % r

def humantime(s):
   h = s // 3600
   s -= 3600*h
   m = s // 60
   s -= 60*m
   return "%02d:%02d:%04.1f" % (h,m,s)

exps_2 = {2**n:n for n in range(256)}

def humanexp(n):
   if n in exps_2:
      return "2e%s" % exps_2[n]
   return str(n)

def humanloss(xy):
   if len(xy) != 2: return str(xy)
   (x, y) = xy
   return "%.2f [iter %s]" % (x, y)

def humanacc(xyz):
   if len(xyz) != 3: return str(xyz)
   (acc, pos, neg) = xyz
   return "%.2f%% (%.2f%% / %.2f%%)" % (100*acc, 100*pos, 100*neg)

def humancounts(xyz):
   if len(xyz) != 3: return str(xyz)
   xyz = tuple(map(humanint, xyz))
   return "%s (%s / %s)" % xyz

UNITS = {
   "count": humanint,
   "loss": humanloss,
   "time": humantime,
   "seconds": lambda x: "%.2f" % x,
   "size": humanbytes,
   "acc": humanacc,
   "counts": humancounts,
}

