import os

DEFAULT_NAME = "strats"
DEFAULT_DIR = os.getenv("PYPROVE_STRATS", DEFAULT_NAME)

def path(pid):
   if pid.startswith("Enigma+"):
      pid = pid.replace("+", "/")[7:]
      root = os.getenv("ENIGMA_ROOT", "./Enigma")
   else:
      root = DEFAULT_DIR
   return os.path.join(root, pid)

def load(pid):
   return open(path(pid)).read().strip()

def save(pid, proto):
   f_pid = path(pid)
   os.makedirs(os.path.dirname(f_pid), exist_ok=True)
   open(f_pid, "w").write(proto.strip())

