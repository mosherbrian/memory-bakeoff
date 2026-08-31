from pathlib import Path
import hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 'vendor/agentmemory/src/state/search-index.ts':'67f3e2ef8f16cbc1108ad9d92e73575f6075c15c',
 'vendor/agentmemory/src/state/vector-index.ts':'d4b8bda760d073cb748967a6744f09d7c95358a1',
 'vendor/agentmemory/src/state/stemmer.ts':'7f210960b67a3178640e5711df47801c14e5d5c3',
 'vendor/agentmemory/src/state/synonyms.ts':'0dab41575c372c23085d982e9884934e556c29d8',
}
ok=True
for rel,want in EXPECTED.items():
 b=(ROOT/rel).read_bytes(); got=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
 print(f'{rel}: {got} {"OK" if got==want else "MISMATCH"}')
 ok &= got==want
sys.exit(0 if ok else 1)
