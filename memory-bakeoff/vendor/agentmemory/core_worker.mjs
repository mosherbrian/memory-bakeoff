import readline from 'node:readline';
import { SearchIndex } from './dist/state/search-index.js';
import { VectorIndex } from './dist/state/vector-index.js';

const RRF_K = 60;
const BM25_WEIGHT = 0.4;
const VECTOR_WEIGHT = 0.6;
const AGREEMENT_BONUS = 0.05;

let bm25 = new SearchIndex();
let vector = new VectorIndex();
let rows = new Map();
let supersededPairs = [];

function tokens(s) {
  const out = new Set();
  for (const t of String(s).normalize('NFC').split(/\s+/)) if (t.length > 2) out.add(t);
  return out;
}
function jaccard(a,b) {
  const na=String(a).normalize('NFC'), nb=String(b).normalize('NFC');
  const A=tokens(na), B=tokens(nb);
  if (!A.size || !B.size) return na.trim().replace(/\s+/g,' ') === nb.trim().replace(/\s+/g,' ') ? 1 : 0;
  let inter=0; for (const x of A) if (B.has(x)) inter++;
  return inter/(A.size+B.size-inter);
}
function safeSlice(text, length) {
  let sliced=String(text).slice(0,length);
  return /[\uD800-\uDBFF]$/.test(sliced) ? sliced.slice(0,-1) : sliced;
}
function observationFor(r) {
  const title=safeSlice(r.text,80);
  return {
    id:r.internal_id, sessionId:'memory', timestamp:r.timestamp ?? null,
    type:'decision', title, subtitle:'', facts:[r.text], narrative:r.text,
    concepts:[], files:[]
  };
}
function removeInternal(id) { bm25.remove(id); vector.remove(id); rows.delete(id); }
function addRecord(r, supersession=true) {
  // Optional mirror of mem::remember's candidate generation + >0.7 Jaccard supersession.
  if (supersession && bm25.size > 0) {
    const hits=bm25.search(r.text,50).filter(h=>h.obsId.startsWith('mem_'));
    for (const h of hits) {
      const prior=rows.get(h.obsId);
      if (prior && jaccard(r.text.toLowerCase(), prior.text.toLowerCase()) > 0.7) {
        const sim=jaccard(r.text.toLowerCase(), prior.text.toLowerCase()); supersededPairs.push({old_record_id:prior.record_id,new_record_id:r.record_id,similarity:sim,old_text:prior.text,new_text:r.text}); removeInternal(h.obsId); break;
      }
    }
  }
  const obs=observationFor(r);
  bm25.add(obs);
  vector.add(r.internal_id,'memory',new Float32Array(r.embedding));
  rows.set(r.internal_id,r);
}
function search(query, qvec, limit) {
  const t0=performance.now();
  const b=bm25.search(query,limit*2);
  const v=vector.search(new Float32Array(qvec),limit*2);
  const scores=new Map();
  b.forEach((r,i)=>scores.set(r.obsId,{bm25Rank:i+1,vectorRank:Infinity,sessionId:r.sessionId,bm25Score:r.score,vectorScore:0}));
  v.forEach((r,i)=>{ const s=scores.get(r.obsId); if(s){s.vectorRank=i+1;s.vectorScore=r.score;} else scores.set(r.obsId,{bm25Rank:Infinity,vectorRank:i+1,sessionId:r.sessionId,bm25Score:0,vectorScore:r.score}); });
  const activeWeight=(b.length?BM25_WEIGHT:0)+(v.length?VECTOR_WEIGHT:0);
  const maxAttainable=activeWeight*(1/(RRF_K+1));
  const ranked=Array.from(scores.entries()).map(([obsId,s])=>{
    const wB=Number.isFinite(s.bm25Rank)?BM25_WEIGHT:0;
    const wV=Number.isFinite(s.vectorRank)?VECTOR_WEIGHT:0;
    const matched=(wB>0?1:0)+(wV>0?1:0);
    const weighted=wB*(1/(RRF_K+s.bm25Rank))+wV*(1/(RRF_K+s.vectorRank));
    const rrf=maxAttainable>0?weighted/maxAttainable:0;
    return {obsId,s,combinedScore:rrf*(1+AGREEMENT_BONUS*(matched-1)),minRank:Math.min(s.bm25Rank,s.vectorRank)};
  });
  ranked.sort((a,b)=>b.combinedScore-a.combinedScore || a.minRank-b.minRank || (a.obsId<b.obsId?-1:a.obsId>b.obsId?1:0));
  const retrievalDepth=Math.max(limit,20);
  const combined=ranked.map(x=>({obsId:x.obsId,sessionId:x.s.sessionId,bm25Score:x.s.bm25Score,vectorScore:x.s.vectorScore,combinedScore:x.combinedScore}));
  const selected=[]; const counts=new Map();
  for(const r of combined){ const c=counts.get(r.sessionId)||0; if(c>=3) continue; selected.push(r); counts.set(r.sessionId,c+1); if(selected.length>=retrievalDepth) break; }
  if(selected.length<retrievalDepth){ for(const r of combined){ if(selected.length>=retrievalDepth) break; if(!selected.some(s=>s.obsId===r.obsId)) selected.push(r); } }
  return {items:selected.slice(0,limit).map(r=>({record_id:rows.get(r.obsId)?.record_id ?? null,...r})), latency_ms:performance.now()-t0, bm25_count:b.length, vector_count:v.length, graph_enabled:false};
}

const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
for await (const line of rl) {
  if(!line.trim()) continue;
  try {
    const m=JSON.parse(line);
    if(m.op==='init') { bm25=new SearchIndex(); vector=new VectorIndex(); rows=new Map(); supersededPairs=[]; const supersession=m.supersession!==false; for(const r of m.records) addRecord(r,supersession); console.log(JSON.stringify({ok:true,count:rows.size,input_count:m.records.length,supersession,superseded_count:supersededPairs.length,superseded_pairs:supersededPairs})); }
    else if(m.op==='search') console.log(JSON.stringify({ok:true,...search(m.query,m.embedding,m.limit??5)}));
    else if(m.op==='close') { console.log(JSON.stringify({ok:true})); process.exit(0); }
    else console.log(JSON.stringify({ok:false,error:'unknown op'}));
  } catch(e) { console.log(JSON.stringify({ok:false,error:String(e?.stack||e)})); }
}
