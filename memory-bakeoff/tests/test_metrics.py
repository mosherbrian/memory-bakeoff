from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.metrics import score_case
from memory_bakeoff.models import RetrievalItem, RetrievalResult


def test_multihop_requires_all_relevant():
    _, cases=build_corpus(); c=next(x for x in cases if x.id=="Q012")
    m=score_case(c,RetrievalResult([RetrievalItem("M017","",1),RetrievalItem("M018","",.9)],1),5)
    assert m.hit_at_k==1
    assert m.all_relevant_at_k==0
    assert m.recall_at_k==2/3


def test_prohibited_is_penalized():
    _, cases=build_corpus(); c=next(x for x in cases if x.id=="Q007")
    m=score_case(c,RetrievalResult([RetrievalItem("M011","",1),RetrievalItem("M012","",.9)],1),5)
    assert m.prohibited_at_k>0
    assert m.prohibited_count==1
    assert m.useful_before_harmful==0


def test_negative_all_relevant_requires_empty_result():
    _, cases=build_corpus(); c=next(x for x in cases if x.id=="Q025")
    empty=score_case(c,RetrievalResult([],1),5)
    noisy=score_case(c,RetrievalResult([RetrievalItem("M048","",.2)],1),5)
    assert empty.all_relevant_at_k == 1
    assert noisy.all_relevant_at_k == 0


def test_context_budget_is_measured_from_returned_text():
    _, cases=build_corpus(); c=next(x for x in cases if x.id=="Q003")
    result=RetrievalResult([RetrievalItem("M005","alpha beta",1),RetrievalItem("M036","gamma",.9)],1)
    m=score_case(c,result,2)
    assert m.returned_chars == len("alpha beta") + len("gamma")
    assert m.returned_words == 3
