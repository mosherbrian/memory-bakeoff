import subprocess,sys
from memory_bakeoff.runner import run_provider

def test_mem0_vendor_hash(): subprocess.run([sys.executable,'scripts/verify_mem0_vendor.py'],check=True)
def test_mem0_core_runs():
 r=run_provider('mem0_core_lsa',distractors=0,top_k=5); assert r['status']=='ok'; assert r['summary']['hit@5']>=0.90
