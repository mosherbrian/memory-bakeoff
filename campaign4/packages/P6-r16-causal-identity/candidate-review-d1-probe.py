import sys,os,tempfile,json,importlib.util
def load(tag,path):
    spec=importlib.util.spec_from_file_location("ce_"+tag,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
NEW=load("new","/home/bmosher/memory-bake-off/campaign4/packages/P6-r16-causal-identity/candidate/src/case_entry.py")
OLD=load("old","/tmp/r16-base-case_entry.py")
d=tempfile.mkdtemp()
def w(name,rec): json.dump(rec,open(os.path.join(d,name+".json"),"w"))
w("itemA",{"onset_at":"2026-09-23T00:51:11Z","provenance":"fixture-producer-seat","uncertainty_s":1})           # missing item
w("itemB",{"item":"other","onset_at":"x","provenance":"p","uncertainty_s":1})                                     # wrong item
w("itemC",{"item":"","onset_at":"x","provenance":"p","uncertainty_s":1})                                          # empty
w("itemD",{"item":None,"onset_at":"x","provenance":"p","uncertainty_s":1})                                        # null
w("itemE",{"item":"itemE","onset_at":"2026-09-23T00:51:11Z","provenance":"fixture-producer-seat","uncertainty_s":1}) # genuine
for tag,m in (("OLD",OLD),("NEW",NEW)):
    print(tag,"missing:",m._read_onset(d,"itemA") is not None,
          "wrong:",m._read_onset(d,"itemB") is not None,
          "empty:",m._read_onset(d,"itemC") is not None,
          "null:",m._read_onset(d,"itemD") is not None,
          "genuine:",m._read_onset(d,"itemE") is not None)
