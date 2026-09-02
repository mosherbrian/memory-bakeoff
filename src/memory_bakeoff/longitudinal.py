"""Frozen, engine-independent Round-2 longitudinal truth ruler (v1)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any, Iterable, Mapping

UTC = timezone.utc
FIXTURE_VERSION = "longitudinal-v1"
SCORER_VERSION = "longitudinal-scorer-v1"
RESULT_SCHEMA_VERSION = "longitudinal-result-v1"

class Transition(StrEnum):
    ADD="ADD"; CONFIG_SELECTION="CONFIG_SELECTION"; SUPERSEDE_CURRENT="SUPERSEDE_CURRENT"; CORRECTION="CORRECTION"; FAILED_ATTEMPT="FAILED_ATTEMPT"; SUCCESSFUL_ATTEMPT="SUCCESSFUL_ATTEMPT"; CONCURRENT_SCOPE="CONCURRENT_SCOPE"; RETRACTION="RETRACTION"; INVALIDATION="INVALIDATION"
class TargetKind(StrEnum):
    CURRENT="current_truth"; SCOPE="scope_truth"; AS_OF="as_of_event_truth"; HISTORICAL_BELIEF="historical_belief"; CORRECTED_HISTORY="corrected_historical_truth"; RECOMMENDED_PROCEDURE="recommended_procedure"; NEGATIVE_UNKNOWN="negative_unknown"; LATE_HISTORY="late_arriving_history"
class FailureClass(StrEnum):
    FUTURE_LEAKAGE="future_leakage"; STALE_PERSISTENCE="stale_persistence"; FALSE_PERSISTENCE="false_persistence"; HISTORY_ERASURE="history_erasure"; SCOPE_COLLAPSE="scope_collapse"; CONFIGURATION_COLLAPSE="configuration_collapse"; FALSE_SUPERSESSION="false_supersession"; CORRECTION_FAILURE="correction_failure"; BELIEF_TRUTH_CONFUSION="belief_truth_confusion"; FAILED_PROCEDURE_ADOPTION="failed_procedure_adoption"; PROCEDURE_RECOMMENDATION_MISSING="procedure_recommendation_missing"; LATE_HISTORY_CORRUPTION="late_history_corruption"; UNKNOWN_HALLUCINATION="unknown_hallucination"; UNSUPPORTED_EVIDENCE="unsupported_evidence"; UNMAPPED_PROVENANCE="unmapped_provenance"; MISSING_REQUIRED_TRUTH="missing_required_truth"
class LifecycleDisposition(StrEnum):
    ACTIVE_CURRENT="active_current"; RETIRED_SUPERSEDED="retired_superseded"; RETIRED_CORRECTED="retired_corrected"; RETRACTED="retracted"; INVALIDATED="invalidated"; DELETED="deleted"; UNKNOWN="unknown"

@dataclass(frozen=True)
class LongitudinalObservation:
    id:str; assertion:str; event_time:datetime; effective_time:datetime; ingestion_order:int; ingestion_time:datetime; scope:str; configuration:str; provenance:str; truth_key:str; transition:Transition; corrects_id:str|None=None; supersedes_id:str|None=None; retracts_id:str|None=None; invalidates_id:str|None=None; procedure_outcome:str|None=None; historical_only:bool=False
    def public_dict(self): return {"canonical_observation_id":self.id,"assertion":self.assertion,"event_time":self.event_time.isoformat(),"effective_time":self.effective_time.isoformat(),"ingestion_order":self.ingestion_order,"ingestion_time":self.ingestion_time.isoformat(),"scope":self.scope,"configuration":self.configuration,"provenance":self.provenance}
    def truth_dict(self):
        d=asdict(self); d.update(event_time=self.event_time.isoformat(),effective_time=self.effective_time.isoformat(),ingestion_time=self.ingestion_time.isoformat(),transition=str(self.transition)); return d
@dataclass(frozen=True)
class Checkpoint: id:str; ingestion_order:int; description:str
@dataclass(frozen=True)
class LongitudinalCase:
    id:str; checkpoint_id:str; target_kind:TargetKind; truth_key:str; query:str; expected_ids:tuple[str,...]; prohibited_ids:tuple[str,...]=(); event_time:datetime|None=None; scope:str|None=None; configuration:str|None=None; rationale:str=""
    def truth_dict(self):
        d=asdict(self); d.update(target_kind=str(self.target_kind),event_time=self.event_time.isoformat() if self.event_time else None); return d
@dataclass(frozen=True)
class LifecycleEvidence: canonical_id:str; active_current:bool|None=None; historically_recoverable:bool|None=None; disposition:LifecycleDisposition=LifecycleDisposition.UNKNOWN; evidence_strength:str="unknown"; native_evidence:str=""
@dataclass(frozen=True)
class LongitudinalFixture:
    observations:tuple[LongitudinalObservation,...]; checkpoints:tuple[Checkpoint,...]; cases:tuple[LongitudinalCase,...]
    def checkpoint(self,id): return next(c for c in self.checkpoints if c.id==id)
    def prefix(self,id): return tuple(o for o in self.observations if o.ingestion_order<=self.checkpoint(id).ingestion_order)
    def public_observations(self,id): return tuple(o.public_dict() for o in self.prefix(id))
@dataclass(frozen=True)
class LongitudinalScore: case_id:str; expected_ids:tuple[str,...]; returned_ids:tuple[str,...]; failure_classes:tuple[str,...]
@dataclass(frozen=True)
class LifecycleScore: checkpoint_id:str; failure_classes:tuple[str,...]; active_expected:tuple[str,...]; historical_expected:tuple[str,...]
@dataclass(frozen=True)
class LongitudinalResultItem: native_id:str|None; native_rank:int; text:str; canonical_id:str|None=None; provenance_exact:bool=False; score:float|None=None
@dataclass(frozen=True)
class LongitudinalResultRecord:
    fixture_version:str; fixture_sha256:str; scorer_contract_sha256:str; system_identity:Mapping[str,str]; repetition:int; checkpoint_id:str; ingested_prefix_sha256:str; case_id:str; requested_limit:int; native_scope_filter:str|None; native_temporal_operation:str|None; items:tuple[LongitudinalResultItem,...]; lifecycle:tuple[LifecycleEvidence,...]=(); reader_answer:str|None=None

def dt(s): return datetime.fromisoformat(s).replace(tzinfo=UTC)
def build_longitudinal_fixture():
    O=LongitudinalObservation; t=dt
    # event/effective time is world validity; ingestion time/order is knowledge visibility.
    obs=(
      O("L001","Nimbus Forge C1 measured 21 t/s.",t("2026-01-10T09:00"),t("2026-01-10T09:00"),1,t("2026-01-10T09:01"),"server:forge","C1","synthetic_public","throughput:forge:C1",Transition.ADD),
      O("L002","Forge selected C1 as active.",t("2026-01-10T09:02"),t("2026-01-10T09:02"),2,t("2026-01-10T09:03"),"server:forge","C1","synthetic_public","active-config:forge",Transition.CONFIG_SELECTION),
      O("L003","Nimbus Forge C2 measured 29 t/s.",t("2026-01-12T09:00"),t("2026-01-12T09:00"),3,t("2026-01-12T09:01"),"server:forge","C2","synthetic_public","throughput:forge:C2",Transition.ADD),
      O("L004","Forge selected C2 as active.",t("2026-01-12T09:02"),t("2026-01-12T09:02"),4,t("2026-01-12T09:03"),"server:forge","C2","synthetic_public","active-config:forge",Transition.SUPERSEDE_CURRENT,supersedes_id="L002"),
      O("L005","Audit corrected Forge C1: valid result was 24 t/s, not 21.",t("2026-01-20T09:00"),t("2026-01-10T09:00"),5,t("2026-01-20T09:01"),"server:forge","C1","synthetic_public","throughput:forge:C1",Transition.CORRECTION,corrects_id="L001"),
      O("L006","Nimbus Anvil C2 measured 33 t/s.",t("2026-01-22T09:00"),t("2026-01-22T09:00"),6,t("2026-01-22T09:01"),"server:anvil","C2","synthetic_public","throughput:anvil:C2",Transition.CONCURRENT_SCOPE),
      O("L007","Forge C2 reproduction without warmup failed.",t("2026-01-23T09:00"),t("2026-01-23T09:00"),7,t("2026-01-23T09:01"),"server:forge","C2","synthetic_public","procedure:forge:C2",Transition.FAILED_ATTEMPT,procedure_outcome="failure"),
      O("L008","Forge C2 reproduction with warmup and fixed batch succeeded.",t("2026-01-24T09:00"),t("2026-01-24T09:00"),8,t("2026-01-24T09:01"),"server:forge","C2","synthetic_public","procedure:forge:C2",Transition.SUCCESSFUL_ATTEMPT,procedure_outcome="success"),
      O("L009","Aurora release branch was release/aurora-1.x.",t("2026-02-01T09:00"),t("2026-02-01T09:00"),9,t("2026-02-01T09:01"),"repo:aurora","main","synthetic_public","branch:aurora",Transition.ADD),
      O("L010","Aurora moved release branch to release/aurora-2.x.",t("2026-02-10T09:00"),t("2026-02-10T09:00"),10,t("2026-02-10T09:01"),"repo:aurora","main","synthetic_public","branch:aurora",Transition.SUPERSEDE_CURRENT,supersedes_id="L009"),
      O("L011","Recovered CI log: Aurora used release/aurora-1.x on Feb 5.",t("2026-02-05T12:00"),t("2026-02-05T12:00"),11,t("2026-02-15T09:01"),"repo:aurora","main","synthetic_public","branch:aurora",Transition.ADD,historical_only=True),
      O("L012","Aurora clients were said to live at internal/gen/aurora_client.go.",t("2026-03-01T09:00"),t("2026-03-01T09:00"),12,t("2026-03-01T09:01"),"repo:aurora","main","synthetic_public","client-path:aurora",Transition.ADD),
      O("L013","Old Aurora client path was invalidated as stale generated artifact.",t("2026-03-03T09:00"),t("2026-03-03T09:00"),13,t("2026-03-03T09:01"),"repo:aurora","main","synthetic_public","client-path:aurora",Transition.INVALIDATION,invalidates_id="L012"),
      O("L014","Aurora clients live at api/gen/aurora/v2/client.go.",t("2026-03-03T09:02"),t("2026-03-03T09:02"),14,t("2026-03-03T09:03"),"repo:aurora","main","synthetic_public","client-path:aurora",Transition.ADD),
      O("L015","A temporary Aurora compatibility symlink exposed old client path.",t("2026-03-04T09:00"),t("2026-03-04T09:00"),15,t("2026-03-04T09:01"),"repo:aurora","main","synthetic_public","compat:aurora",Transition.ADD),
      O("L016","Aurora removed temporary compatibility symlink; claim retracted.",t("2026-03-05T09:00"),t("2026-03-05T09:00"),16,t("2026-03-05T09:01"),"repo:aurora","main","synthetic_public","compat:aurora",Transition.RETRACTION,retracts_id="L015"))
    cps=tuple(Checkpoint(f"CP{n:02d}",n,f"after ingestion {n}") for n in (1,4,5,6,8,10,11,14,16)); C=LongitudinalCase
    cases=(
      C("LQ01","CP01",TargetKind.CURRENT,"throughput:forge:C1","Forge/C1 throughput",("L001",),scope="server:forge",configuration="C1"), C("LQ02","CP04",TargetKind.CURRENT,"active-config:forge","Active Forge config",("L004",),("L002",),scope="server:forge",configuration="C2"), C("LQ03","CP04",TargetKind.SCOPE,"throughput:forge:C1","Forge/C1 remains",("L001",),("L003",),scope="server:forge",configuration="C1"),
      C("LQ04","CP04",TargetKind.AS_OF,"throughput:forge:C1","As of Jan 10 Forge/C1",("L001",),event_time=t("2026-01-10T10:00"),scope="server:forge",configuration="C1"), C("LQ05","CP05",TargetKind.AS_OF,"throughput:forge:C1","As of Jan 10 corrected Forge/C1",("L005",),("L001",),event_time=t("2026-01-10T10:00"),scope="server:forge",configuration="C1"), C("LQ06","CP05",TargetKind.HISTORICAL_BELIEF,"throughput:forge:C1","Belief at CP01",("L001",),("L005",),event_time=t("2026-01-10T10:00"),scope="server:forge",configuration="C1"), C("LQ07","CP05",TargetKind.CORRECTED_HISTORY,"throughput:forge:C1","Corrected truth Jan 10",("L005",),("L001",),event_time=t("2026-01-10T10:00"),scope="server:forge",configuration="C1"),
      C("LQ08","CP06",TargetKind.SCOPE,"throughput:forge:C2","Forge C2 not Anvil",("L003",),("L006",),scope="server:forge",configuration="C2"), C("LQ09","CP06",TargetKind.SCOPE,"throughput:anvil:C2","Anvil C2 not Forge",("L006",),("L003",),scope="server:anvil",configuration="C2"), C("LQ10","CP08",TargetKind.RECOMMENDED_PROCEDURE,"procedure:forge:C2","Recommended procedure",("L008",),("L007",),scope="server:forge",configuration="C2"),
      C("LQ11","CP10",TargetKind.CURRENT,"branch:aurora","Current Aurora branch",("L010",),("L009",),scope="repo:aurora",configuration="main"), C("LQ12","CP11",TargetKind.CURRENT,"branch:aurora","Current after recovered history",("L010",),("L009","L011"),scope="repo:aurora",configuration="main"), C("LQ13","CP11",TargetKind.LATE_HISTORY,"branch:aurora","Aurora branch Feb 5",("L011",),event_time=t("2026-02-05T23:00"),scope="repo:aurora",configuration="main"),
      C("LQ14","CP14",TargetKind.CURRENT,"client-path:aurora","Current Aurora client path",("L014",),("L012",),scope="repo:aurora",configuration="main"), C("LQ15","CP16",TargetKind.CURRENT,"compat:aurora","Current compat symlink",(),("L015",),scope="repo:aurora",configuration="main"), C("LQ16","CP04",TargetKind.NEGATIVE_UNKNOWN,"unknown:oncall","Nimbus on call",(),scope="server:forge",configuration="C2"), C("LQ17","CP01",TargetKind.CURRENT,"throughput:forge:C1","Pre-future C1",("L001",),scope="server:forge",configuration="C1"), C("LQ18","CP14",TargetKind.HISTORICAL_BELIEF,"client-path:aurora","Recorded old client path",("L012",),("L013","L014"),event_time=t("2026-03-01T10:00"),scope="repo:aurora",configuration="main"), C("LQ19","CP14",TargetKind.CORRECTED_HISTORY,"client-path:aurora","Verified client path",("L014",),("L012",),event_time=t("2026-03-01T10:00"),scope="repo:aurora",configuration="main"), C("LQ20","CP16",TargetKind.AS_OF,"branch:aurora","Aurora Feb 5",("L011",),("L010",),event_time=t("2026-02-05T23:00"),scope="repo:aurora",configuration="main"))
    return LongitudinalFixture(obs,cps,cases)

def byid(f): return {o.id:o for o in f.observations}
def expected_lifecycle_state(f,checkpoint_id):
    vis=f.prefix(checkpoint_id); out={}
    for o in vis:
      later=next((x for x in vis if o.id in (x.corrects_id,x.supersedes_id,x.retracts_id,x.invalidates_id)),None)
      active=not o.historical_only and not later and o.transition not in (Transition.CORRECTION,Transition.INVALIDATION,Transition.RETRACTION,Transition.FAILED_ATTEMPT,Transition.SUCCESSFUL_ATTEMPT)
      disposition=LifecycleDisposition.ACTIVE_CURRENT if active else ({Transition.CORRECTION:LifecycleDisposition.RETIRED_CORRECTED,Transition.SUPERSEDE_CURRENT:LifecycleDisposition.RETIRED_SUPERSEDED,Transition.INVALIDATION:LifecycleDisposition.INVALIDATED,Transition.RETRACTION:LifecycleDisposition.RETRACTED}.get(later.transition if later else None,LifecycleDisposition.UNKNOWN))
      out[o.id]=LifecycleEvidence(o.id,active,True,disposition,"harness_truth")
    return out
def oracle_expected_ids(f,c): return c.expected_ids
def score_longitudinal_case(f,c,returned_ids):
    r=tuple(returned_ids); b=byid(f); visible={o.id for o in f.prefix(c.checkpoint_id)}; fail=set(); known=[x for x in r if x in b]
    if any(x not in b for x in r): fail.add(FailureClass.UNMAPPED_PROVENANCE)
    if any(x not in visible for x in known): fail.add(FailureClass.FUTURE_LEAKAGE)
    if c.expected_ids and not set(c.expected_ids)&set(r):
      fail.add(FailureClass.HISTORY_ERASURE if c.target_kind in (TargetKind.HISTORICAL_BELIEF,TargetKind.AS_OF,TargetKind.LATE_HISTORY) else FailureClass.PROCEDURE_RECOMMENDATION_MISSING if c.target_kind is TargetKind.RECOMMENDED_PROCEDURE else FailureClass.MISSING_REQUIRED_TRUTH)
      if c.target_kind in (TargetKind.CORRECTED_HISTORY,TargetKind.AS_OF): fail.add(FailureClass.CORRECTION_FAILURE)
    if not c.expected_ids and r: fail.add(FailureClass.UNSUPPORTED_EVIDENCE)
    bad=set(c.prohibited_ids)&set(r)
    if bad:
      if c.target_kind is TargetKind.HISTORICAL_BELIEF: fail.add(FailureClass.BELIEF_TRUTH_CONFUSION)
      elif c.target_kind is TargetKind.RECOMMENDED_PROCEDURE: fail.add(FailureClass.FAILED_PROCEDURE_ADOPTION)
      elif c.target_kind is TargetKind.CORRECTED_HISTORY or c.truth_key=="client-path:aurora": fail.add(FailureClass.FALSE_PERSISTENCE)
      elif any(b[x].scope!=c.scope for x in bad): fail.add(FailureClass.SCOPE_COLLAPSE)
      elif any(b[x].configuration!=c.configuration for x in bad): fail.add(FailureClass.CONFIGURATION_COLLAPSE)
      else: fail.add(FailureClass.STALE_PERSISTENCE)
    if c.target_kind is TargetKind.CURRENT and any(b.get(x) and b[x].historical_only for x in r): fail.add(FailureClass.LATE_HISTORY_CORRUPTION)
    return LongitudinalScore(c.id,c.expected_ids,r,tuple(sorted(map(str,fail))))
def score_answer_claim(c,*,assertion_supported): return () if c.target_kind is not TargetKind.NEGATIVE_UNKNOWN or assertion_supported else (str(FailureClass.UNKNOWN_HALLUCINATION),)
def score_lifecycle_state(f,checkpoint_id,observed):
    expected=expected_lifecycle_state(f,checkpoint_id); actual={x.canonical_id:x for x in observed}; fails=set()
    for id,want in expected.items():
      got=actual.get(id)
      if got and want.active_current and got.active_current is False: fails.add(FailureClass.FALSE_SUPERSESSION)
      if got and want.historically_recoverable and got.historically_recoverable is False: fails.add(FailureClass.HISTORY_ERASURE)
    return LifecycleScore(checkpoint_id,tuple(sorted(map(str,fails))),tuple(sorted(x for x,v in expected.items() if v.active_current)),tuple(sorted(x for x,v in expected.items() if v.historically_recoverable)))
def aggregate_failure_classes(scores):
    out={str(x):0 for x in FailureClass}
    for s in scores:
      for x in s.failure_classes:
       if x in out: out[x]+=1
    return out
def canonical_json(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def fixture_payload(f=None):
    f=f or build_longitudinal_fixture(); return {"fixture_version":FIXTURE_VERSION,"observations":[o.truth_dict() for o in f.observations],"checkpoints":[asdict(c) for c in f.checkpoints],"cases":[c.truth_dict() for c in f.cases]}
def fixture_sha256(f=None): return hashlib.sha256(canonical_json(fixture_payload(f)).encode()).hexdigest()
def result_contract_payload(): return {"scorer_version":SCORER_VERSION,"result_schema_version":RESULT_SCHEMA_VERSION,"target_kinds":[str(x) for x in TargetKind],"failure_classes":[str(x) for x in FailureClass],"result_fields":list(LongitudinalResultRecord.__dataclass_fields__),"item_fields":list(LongitudinalResultItem.__dataclass_fields__),"lifecycle_fields":list(LifecycleEvidence.__dataclass_fields__),"rules":{"truth_key_private":True,"no_harness_post_filtering":True,"unknown_id_not_future":True,"active_absence_not_deletion":True,"raw_retrieval_not_hallucination":True}}
def scorer_contract_sha256(): return hashlib.sha256(canonical_json(result_contract_payload()).encode()).hexdigest()
def ruler_manifest(f=None):
    f=f or build_longitudinal_fixture(); return {"fixture_version":FIXTURE_VERSION,"fixture_sha256":fixture_sha256(f),"scorer_version":SCORER_VERSION,"scorer_contract_sha256":scorer_contract_sha256(),"result_schema_version":RESULT_SCHEMA_VERSION,"observation_count":len(f.observations),"checkpoint_count":len(f.checkpoints),"case_count":len(f.cases),"anti_query_fit":"After any contestant uses longitudinal-v1, no v1 fixture/query/truth/scorer semantic change is permitted; repairs require v2."}
