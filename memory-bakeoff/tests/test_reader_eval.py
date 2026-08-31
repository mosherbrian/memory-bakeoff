from __future__ import annotations

from memory_bakeoff.reader_eval import ANSWER_SPECS, score_answer, run_reader_eval
from memory_bakeoff.llm.base import LLMClient, LLMResponse, LLMUsage


class OracleishFake(LLMClient):
    name="oracleish-test"
    def complete(self,request):
        text=request.messages[-1].content
        if "current build coordinator" in text: answer="strix07"
        elif "root password" in text: answer="INSUFFICIENT_MEMORY"
        else: answer="INSUFFICIENT_MEMORY"
        return LLMResponse(answer,"oracleish-test","stop",LLMUsage(),request_id=request.request_id)


def spec(case_id): return next(x for x in ANSWER_SPECS if x.case_id==case_id)


def test_exact_answer_passes_and_stale_answer_fails():
    ok=score_answer(spec("Q007"),"strix07",provider="x",retrieved_ids=["M012"],request_id="r")
    bad=score_answer(spec("Q007"),"Use strix07, not strix03.",provider="x",retrieved_ids=["M012","M011"],request_id="r")
    assert ok.pass_answer
    assert not bad.pass_answer
    assert bad.prohibited_hits == ("strix03",)


def test_negative_requires_explicit_insufficient():
    assert score_answer(spec("Q025"),"INSUFFICIENT_MEMORY",provider="x",retrieved_ids=[],request_id="r").pass_answer
    assert not score_answer(spec("Q025"),"I don't know",provider="x",retrieved_ids=[],request_id="r").pass_answer


def test_reader_eval_uses_provider_context_and_deterministic_grader():
    result=run_reader_eval(["bm25"],OracleishFake(),specs=(spec("Q007"),spec("Q025")))
    assert result["provider_summary"]["bm25"]["answer_pass_rate"] == 1.0
    assert len(result["details"]) == 2
