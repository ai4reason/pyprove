import os
import logging

from . import problem
from . import strategy
from . import output
from . import results
from . import solved
from ..par import apply
from ..bar import SolvedBar
from .. import log, human

logger = logging.getLogger(__name__)

def prove1(prover, problem, f_problem, strat, f_out):
   result = prover.prove(f_problem, strat, f_out=f_out)
   return (problem, result)

def eval1(prover, bid, sid, cores, options=[], label="[*]", **others):
   results1 = results.load(prover, bid, sid) if "force" not in options else {}
   probs = problem.problems(bid)
   probs = [p for p in probs if p not in results1]
   if not probs:
      logger.info(f"- allready evaluated: {sid} @ {bid}")
      return results1

   def callback(pr, bar):
      nonlocal results1, prover
      (problem, result) = pr
      if bar and prover.solved(result):
         bar.inc_solved()
      results1[problem] = result

   strat = strategy.load(sid)
   args = [(
         prover,
         p,
         problem.path(bid, p), 
         strat, 
         output.path(prover, bid, sid, p, options=options)) 
      for p in probs]
   if "headless" not in options:
      bar = SolvedBar(label, max=len(probs), tail=sid) 
   else:
      bar = None
      logger.info(f"- evaluating {sid} @ {bid}")

   apply(prove1, args, cores=cores, callback=callback, bar=bar)
   results.save(prover, bid, sid, results1)
   solved.save(prover, bid, sid, results1)
   return results1

def evals(prover, bids, sids, cores=4, **others):
   allres = {}
   ns = len(bids) * len(sids)
   ps = sum([len(problem.problems(bid)) for bid in bids]) * len(sids)
   logger.info("+ evaluating %s strategies on %d benchmarks" % (len(sids), len(bids)))
   logger.debug(log.data("- evaluation parameters:", dict(
      bids=bids, 
      sids=sids,
      cores=cores,
      prover=prover.name(),
      resources=prover.resources(),
      problems=human.humanint(ps),
      eta=human.humantime(ps*prover.timeout()/cores) if prover.timeout() else "unknown",
   )))
   
   n = 1
   label = "(%%3d/%d)" % ns
   for bid in bids:
      for sid in sids:
         result1 = eval1(prover, bid, sid, cores=cores, label=label%n, **others)
         n += 1
         result1 = {(bid,sid,p):result1[p] for p in result1}
         allres.update(result1)
   return allres

