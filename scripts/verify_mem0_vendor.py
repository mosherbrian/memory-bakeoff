from pathlib import Path
import hashlib,sys
p=Path(__file__).resolve().parents[1]/'vendor/mem0/mem0/utils/scoring.py'
b=p.read_bytes(); got=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest(); want='e85a9cb8e8b263dbab898faa07578044c0a07386'
print(f'{p}: {got} {"OK" if got==want else "MISMATCH"}')
sys.exit(got!=want)
