# External state-update audit

Scope: DESIGN/AUDIT ONLY. No run. No composite build. Cost: $0, local reads only.

ANSWER Q4's named next step is to audit external state-update mechanisms and existing evidence before proposing a substantively different protection experiment. This advances G2 supersession and R-PF Decision Gate F.

No prior external state-update mechanism audit existed. This receipt adds no new measurements.

The tested key-equality protection is retired because its measured effect worsens false replacement.

## Prior measurement

team/S11-LAYER-HIST/verdict.json: native 22/33 false replacement; tested layer 33/33 false replacement; 0/13 missed. The layer worsens it.

team/S7-STATELAYER/verdict.json: controlled 0/32 in both arms.

team/S10-PI-LCM-HIST/verdict.json: native 22/33 false replacement; 0/13 missed.

## agentmemory

Source: team/EXTERNAL-AGENT-MEMORY-ATLAS-20260917.md.

Update model: Records can be replaced or retained; the card does not establish how a conflicting new fact supersedes an old record, so version precedence for this mechanism remains unknown.

Availability: public repository; local source access is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for agentmemory. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Hindsight

Source: team/EXTERNAL-MEMPALACE-20260919.md.

Update model: Retained facts can be consolidated; whether a correction invalidates the old fact is not established by the available card, so retention semantics stay unverified.

Availability: public repository; local source access is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for Hindsight. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Mem0

Source: team/EXTERNAL-HEIMDALL-20260917.md.

Update model: An update may replace an existing memory record; the card leaves conflict resolution and retention of previous values unverified, so overwrite behavior is not established.

Availability: public repository; local source access is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for Mem0. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## MemPalace

Source: team/EXTERNAL-MEMPALACE-20260919.md.

Update model: Old and new facts are retained; timing details are not established by the reviewed card.

Availability: public repository; local source access is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for MemPalace. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Engram Alpha

Source: team/EXTERNAL-ENGRAM-ALPHA-20260917.md.

Update model: The discovery card states no update semantics; how stored facts are revised or retained is undocumented and unverified.

Availability: unknown; no availability statement was found in the reviewed card.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for Engram Alpha. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## mex

Source: team/EXTERNAL-MEX-20260919.md.

Update model: A repo-local code graph plus a living Markdown wiki retain versioned files; whether wiki edits supersede or append is undocumented in the reviewed card.

Availability: local repository installation is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for mex. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Munder Difflin

Source: team/EXTERNAL-MUNDER-DIFFLIN-20260920.md.

Update model: A shipped multi-agent harness with cross-session memory retains prior session material; its supersession and expiry rules are not established by the reviewed card.

Availability: installable harness; local installation is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for Munder Difflin. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Procedural Graphs

Source: team/EXTERNAL-PROCEDURAL-GRAPHS-20260920.md.

Update model: Versioned procedure graphs retain prior revisions; how a new graph version invalidates an old one is not established by the reviewed card.

Availability: paper artifact; local reading is possible.

Licence: unknown; the card does not establish redistribution terms.

Fleet evidence: no direct fleet measurement exists for Procedural Graphs. The prior native and layer runs above are not evaluations of this product; external descriptions are not fleet results.

## Cards reviewed

EXTERNAL-ADEBENCH-20260917.md, EXTERNAL-AGENT-MEMORY-ATLAS-20260917.md, EXTERNAL-CHEAP-CLASSIFIER-GATING-20260919.md, EXTERNAL-CORPORA-RECOMMENDATION.md, EXTERNAL-ENGRAM-ALPHA-20260917.md, EXTERNAL-GVS5H-LEDGER-20260921.md, EXTERNAL-HEIMDALL-20260917.md, EXTERNAL-KNOWLEDGEDRIFT-20260916.md, EXTERNAL-MEMPALACE-20260919.md, EXTERNAL-MEX-20260919.md, EXTERNAL-MUNDER-DIFFLIN-20260920.md, EXTERNAL-PROCEDURAL-GRAPHS-20260920.md, EXTERNAL-TDFLOW-20260921.md.

## Final disposition

For now, none yet passes into experiment candidacy because update models are unverified against fleet measurements; the key-equality class stays closed.
