from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[1]/"vendor"/"membukkit"/"src"/"membukkit"
EXPECTED={
 "config.py":"ffef9fe8649fd9a3d59bc88cee1447930689fd90",
 "time_utils.py":"6dd31a6e5b1f26e02c118454797af3107a318cad",
 "storage/base.py":"933015fd6e78cbdbedd3bdee4beef7280ac49f85",
 "storage/memory.py":"e3256902ac9e054377b2e167af43372b1d17f73a",
 "retrieval/bucket_index.py":"b6dba922cb9409c16db8f530c61b88308230bed6",
 "retrieval/buckets.py":"5cd4c114b9cbf9e121b25e0d72dab6d9c54550e5",
 "retrieval/router.py":"cfca79b838eb1494798c1ef4423a7e59557b2f7f",
 "supersession.py":"319556707aea9468816efcfffff0ed8781cd48d6",
 "pipeline.py":"295893c704e6582f9f979c007439e60eed92e0e3",
}

def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

bad=[]
for rel,expected in EXPECTED.items():
    p=ROOT/rel; actual=git_blob_sha(p.read_bytes()) if p.exists() else "MISSING"
    mark="OK" if actual==expected else "FAIL"
    print(f"{mark:4} {rel:32} {actual}")
    if actual!=expected: bad.append((rel,expected,actual))
if bad:
    raise SystemExit(f"{len(bad)} vendored MemBukkit file(s) differ from pinned upstream")
print(f"verified {len(EXPECTED)} MemBukkit semantic files")
