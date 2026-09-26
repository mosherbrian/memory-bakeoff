// Trial-only request accounting inherited by headless reflection processes.
// No prompts, credentials or response content are logged.
import fs from 'node:fs';
import {zstdDecompressSync} from 'node:zlib';
const base='/trial-control';
let nativeFetch=globalThis.fetch;
function locked(fn){
  let acquired=false;
  for(let i=0;i<500;i++){try{fs.mkdirSync(base+'/lock');acquired=true;break;}catch{Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,10);}}
  if(!acquired)throw new Error('TRIAL counter lock unavailable');
  try{let state=JSON.parse(fs.readFileSync(base+'/usage.json','utf8'));const result=fn(state);fs.writeFileSync(base+'/usage.json',JSON.stringify(state));return result;}finally{fs.rmdirSync(base+'/lock');}
}
const guardedFetch=async function(input,options){
  const url=new URL(typeof input==='string'?input:input instanceof URL?input.href:input.url);
  if(url.hostname!=='chatgpt.com' && url.hostname!=='auth.openai.com')throw new Error('TRIAL disallowed fetch host: '+url.hostname);
  const modelCall=url.pathname.includes('/responses');
  if(!modelCall)return nativeFetch(input,options);
  let raw=options?.body;
  if(raw instanceof Uint8Array){raw=zstdDecompressSync(raw).toString();}
  const body=typeof raw==='string'?JSON.parse(raw):{};
  if(body.model!=='gpt-5.6-sol')throw new Error('TRIAL model mismatch: '+body.model);
  const call=locked(s=>{
    if(Date.now()>s.deadline_ms || s.calls>=30 || s.input_tokens>=250000 || s.output_tokens>=20000)throw new Error('TRIAL resource limit reached');
    s.calls++;s.requests.push({n:s.calls,at:new Date().toISOString(),model:body.model,reasoning:body.reasoning?.effort??null,pid:process.pid});return s.calls;
  });
  const response=await nativeFetch(input,options);
  if(!response.body)return response;
  const decoder=new TextDecoder();let pending='',usage=null,recorded=false;
  function record(){if(recorded)return;recorded=true;locked(s=>{s.responses.push({n:call,status:response.status,usage});if(usage){s.input_tokens+=usage.input_tokens??0;s.output_tokens+=usage.output_tokens??0;}else{s.missing_usage++;}});}
  const stream=response.body.pipeThrough(new TransformStream({
    transform(chunk,controller){
      pending+=decoder.decode(chunk,{stream:true});
      const lines=pending.split('\n');pending=lines.pop();
      for(const line of lines){if(!line.startsWith('data: '))continue;try{const event=JSON.parse(line.slice(6));const u=event.response?.usage??event.usage;if(u){usage=u;record();}}catch{}}
      controller.enqueue(chunk);
    },
    flush(){record();}
  }));
  return new Response(stream,{status:response.status,statusText:response.statusText,headers:response.headers});
};
Object.defineProperty(globalThis,'fetch',{configurable:false,get(){return guardedFetch;},set(v){if(v!==guardedFetch)nativeFetch=v;}});
// Both runtimes support SSE fallback; count the same HTTP boundary in all workers.
Object.defineProperty(globalThis,'WebSocket',{configurable:false,get(){return undefined;},set(_v){}});
