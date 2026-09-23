import sys; sys.path.insert(0,"/tmp/p8qual")
from driver import setup,run,endturn,wakes,say
d,calls=setup("B2",seats={"kiln":"K","corvid":"K","tern":"T"})
for args in (["dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v"],
             ["run","--config","cfg.json","--once"],
             ["status","--config","cfg.json"]):
    rc,o,e=run(d,*args); say(args[0],"rc",rc,"out",o[:200],"err",e[:300])
open(d+"/art/out.bin","w").write("hello")
say("claim",run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin"))
say("manual status",run(d,"status","--config","cfg.json"))
