from . import results

def summary(bids, sids, ref=None, **others):
   msg = ""
   def text(m=""):
      nonlocal msg
      msg += m + "\n"
   text("Summary @ %s:" % bids)
   if not ref:
      ref = sids[0]
   data = results.summary(bids=bids, sids=sids, ref=ref, **others) 
   for sid in sorted(data, key=lambda s: data[s][2], reverse=True):
      s = data[sid]
      if ref and len(s) >=5:
         text("%s %4s/%4s   +%2s/-%2s: %s" % ("!" if s[1] else "",s[2],s[0],s[3],s[4],sid))
      else:
         text("%s %4s/%4s: %s" % ("!" if s[1] else "",s[2],s[0],sid))
   return msg.strip("\n")

