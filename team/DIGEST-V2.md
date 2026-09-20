# DIGEST-V2 — model curation pass over the 318-group digest

**Author:** worker-glm-2 (implementer) · **Date:** 2026-09-14 · **Spec:** `dispatch/DIGEST-V2-PASS.md` (Brian 2026-09-14: v1 skews machine-probe, needs model pass before vault seeding)
**Inputs (local-only):** `transcript-mining/full-20260913/durable-facts.jsonl` (324) + `digest.md` (318 groups v1) + `team/TRANSCRIPT-MINING-FULL.md`
**Method:** deterministic local classifier (rule cascade: probe-patterns → question → fuzzy-hedge → fact-residual), three tightening passes. No vault writes. No raw transcript reads beyond the two input files.
**Gate:** Cairn (worker-pi) 20-row spot-check required before serving to Brian.

## Counts

| shape | n | verdict | n |
|---|---|---|---|
| fact (crisp, vault-ready as written) | 32 | seed | 32 |
| probe (machine-verification material) | 193 | probe-corpus | 193 |
| question (open, unresolvable) | 18 | drop | 93 |
| fuzzy (hedged, needs confidence) | 75 | | |

Heads-up for Brian: only **32/318 (10%)** survive as vault candidates — confirms the skew call. The bulk (**193** probe) is invocation/outcome test material, not vault prose.

## Seed rows (fact → seed, with v1 source pointers)

### v1-#106 [convention, seen 1x in 1 session(s)]
- rewrite: We should review our model params that we settled on previously.
- v1 text: We should review our model params that we settled on previously.
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:35733

### v1-#108 [env_fact, seen 1x in 1 session(s)]
- rewrite: While we wait, one thing that I considered a while back that we discussed as a nice project was the idea of an inference-aware smart load balancer.
- v1 text: While we wait, one thing that I considered a while back that we discussed as a nice project was the idea of an inference-aware smart load balancer. Now that we are close to having a tuned practical AI workflow, it would 
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:38799

### v1-#110 [env_fact, seen 1x in 1 session(s)]
- rewrite: That implies we need to set iommu=pt here for this to be a proper test representation of those production boxes.
- v1 text: That implies we need to set iommu=pt here for this to be a proper test representation of those production boxes.
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:42563

### v1-#117 [env_fact, seen 1x in 1 session(s)]
- rewrite: Okay, I have a few questions looking at http://strix-halo.local:8090/drift 1.
- v1 text: Okay, I have a few questions looking at http://strix-halo.local:8090/drift 1. Fleet: declared vs observed No drift. Every declared fact about every box was observed and matches — build, RAM, services, memlock, model SHAs
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:54308

### v1-#123 [env_fact, seen 1x in 1 session(s)]
- rewrite: @"/home/bmosher/.claude/uploads/cf72207b-8cc8-4991-9026-7fbc2fd10d7a/bcb94a36-Laguna_S_2.1__How_Agent_Harnesses_and_Inference_Budgets_Shape_Coding_Performance.pdf"
- v1 text: @"/home/bmosher/.claude/uploads/cf72207b-8cc8-4991-9026-7fbc2fd10d7a/bcb94a36-Laguna_S_2.1__How_Agent_Harnesses_and_Inference_Budgets_Shape_Coding_Performance.pdf"
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:63551

### v1-#134 [env_fact, seen 1x in 1 session(s)]
- rewrite: REFUSING: /var/home/bmosher/nathanw-v04/vulkan build has no --spec-type; MTP will not work.
- v1 text: REFUSING: /var/home/bmosher/nathanw-v04/vulkan build has no --spec-type; MTP will not work. Use a newer build.
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:66976

### v1-#136 [env_fact, seen 1x in 1 session(s)]
- rewrite: The script couldn't find hf.
- v1 text: The script couldn't find hf. I did a find: /home/bmosher/.local/opt/hf-venv/bin/hf
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:67073

### v1-#143 [env_fact, seen 1x in 1 session(s)]
- rewrite: So sending a new turn message too quickly after compaction caused it?
- v1 text: So sending a new turn message too quickly after compaction caused it? You say that the interruption did not cause me time, but I saw the server prefilling *slowly* right here: 73.46.833.198 I slot print_timing: id 2 \| ta
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:69959

### v1-#152 [env_fact, seen 1x in 1 session(s)]
- rewrite: $ systemctl show user@$(id -u).service -p LimitMEMLOCK LimitMEMLOCK=8388608
- v1 text: $ systemctl show user@$(id -u).service -p LimitMEMLOCK LimitMEMLOCK=8388608
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:78001

### v1-#159 [env_fact, seen 1x in 1 session(s)]
- rewrite: So we will be putting our models in /opt/ai/models/
- v1 text: So we will be putting our models in /opt/ai/models/
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:79203

### v1-#161 [env_fact, seen 1x in 1 session(s)]
- rewrite: /var/home/bmosher/flm-npu/deploy-flm-npu.sh: line 62: PUBLIC_PORT: unbound variable
- v1 text: /var/home/bmosher/flm-npu/deploy-flm-npu.sh: line 62: PUBLIC_PORT: unbound variable
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:79270

### v1-#162 [env_fact, seen 1x in 1 session(s)]
- rewrite: Failed to connect to user scope bus via local transport: $DBUS_SESSION_BUS_ADDRESS and $XDG_RUNTIME_DIR not defined (consider using --machine=<user>@.host --user to connect to bus of other user)
- v1 text: Failed to connect to user scope bus via local transport: $DBUS_SESSION_BUS_ADDRESS and $XDG_RUNTIME_DIR not defined (consider using --machine=<user>@.host --user to connect to bus of other user)
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:79291

### v1-#163 [env_fact, seen 1x in 1 session(s)]
- rewrite: I ran the script with FLM_HOME=/var/opt/ai/flm and it should have been FLM_HOME=/var/opt/ai/models/flm.
- v1 text: I ran the script with FLM_HOME=/var/opt/ai/flm and it should have been FLM_HOME=/var/opt/ai/models/flm. Now the unit can't find the models directory.
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:79330

### v1-#164 [env_fact, seen 1x in 1 session(s)]
- rewrite: sudo printf '[Service]\nLimitMEMLOCK=infinity\n' > /etc/systemd/system/user@$(id -u svc-cdsbb-aa).service.d/memlock.conf Permission denied
- v1 text: sudo printf '[Service]\nLimitMEMLOCK=infinity\n' > /etc/systemd/system/user@$(id -u svc-cdsbb-aa).service.d/memlock.conf Permission denied
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:79426

### v1-#171 [env_fact, seen 1x in 1 session(s)]
- rewrite: I'm getting a in-between turn delay for some reason: iming: id 3 \| task 9282 \| draft acceptance = 0.77295 ( 160 accepted / 207 generated), mean len = 3.32 82.34.444.066 I slot release: id 3 \| task 9282 \| stop processing:
- v1 text: I'm getting a in-between turn delay for some reason: iming: id 3 \| task 9282 \| draft acceptance = 0.77295 ( 160 accepted / 207 generated), mean len = 3.32 82.34.444.066 I slot release: id 3 \| task 9282 \| stop processing:
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:87813

### v1-#193 [env_fact, seen 1x in 1 session(s)]
- rewrite: I saw the session spinning for a while and the log had this sort of thing in it: 200.32.882.879 I slot launch_slot_: id 3 \| task 4530 \| processing task, is_child = 0 200.32.883.931 W slot operator(): id 3 \| task 4530 \| o
- v1 text: I saw the session spinning for a while and the log had this sort of thing in it: 200.32.882.879 I slot launch_slot_: id 3 \| task 4530 \| processing task, is_child = 0 200.32.883.931 W slot operator(): id 3 \| task 4530 \| o
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:92266

### v1-#200 [env_fact, seen 1x in 1 session(s)]
- rewrite: Here's the 5411 logs: 129.14.904.978 I slot print_timing: id 3 \| task 11551 \| total time = 41911.47 ms / 982 tokens 129.14.904.980 I slot print_timing: id 3 \| task 11551 \| graphs reused = 10389 129.14.904.989 I slot prin
- v1 text: Here's the 5411 logs: 129.14.904.978 I slot print_timing: id 3 \| task 11551 \| total time = 41911.47 ms / 982 tokens 129.14.904.980 I slot print_timing: id 3 \| task 11551 \| graphs reused = 10389 129.14.904.989 I slot prin
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:93056

### v1-#211 [env_fact, seen 1x in 1 session(s)]
- rewrite: kernel=balanced PPT=8 W ▕thche▕ saved original tuned profile: balanced ▕ ▕ applying tuned profile: throughput-performance ▕lawdb▕ after : tuned=throughput-performance kernel=performanc▕ ▕ e PPT=18 W ▕-heal▕ VER
- v1 text: kernel=balanced PPT=8 W ▕thche▕ saved original tuned profile: balanced ▕ ▕ applying tuned profile: throughput-performance ▕lawdb▕ after : tuned=throughput-performance kernel=performanc▕ ▕ e PPT=18 W ▕-heal▕ VER
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:95752

### v1-#216 [env_fact, seen 1x in 1 session(s)]
- rewrite: Addendum 3 is excellent.
- v1 text: Addendum 3 is excellent. Addendum 4 contains one new inference error that I would fix before freezing this. And it is exactly the same species of error this investigation has been teaching: counting operations is not mea
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:103582

### v1-#228 [env_fact, seen 1x in 1 session(s)]
- rewrite: Speaking of prefills, I canceled a turn and got swapped to a different slot.
- v1 text: Speaking of prefills, I canceled a turn and got swapped to a different slot. Was this someone else hitting the box? 119.55.507.818 I slot print_timing: id 3 \| task 6563 \| n_decoded = 235, tg = 19.82 t/s, tg_3s = 22.61 t/
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:108676

### v1-#233 [env_fact, seen 1x in 1 session(s)]
- rewrite: Summary Deployed 38237d2 + dd4fa41 (PID 1196864, commit dd4fa41).
- v1 text: Summary Deployed 38237d2 + dd4fa41 (PID 1196864, commit dd4fa41). The immortal-pin bug is fixed and verified end-to-end: - Root cause (confirmed): affinity.json stored time.monotonic() readings. On restart the monotonic 
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:109621

### v1-#236 [env_fact, seen 1x in 1 session(s)]
- rewrite: 0.00.071.274 I srv load_model: loading model '/opt/ai/models/qwen3.8-27b/Qwen3.8-27B-Q4_K_M.gguf' 0.00.465.552 E llama_model_load: error loading model: done_getting_tensors: wrong number of tensors; expected 81, got 58 0
- v1 text: 0.00.071.274 I srv load_model: loading model '/opt/ai/models/qwen3.8-27b/Qwen3.8-27B-Q4_K_M.gguf' 0.00.465.552 E llama_model_load: error loading model: done_getting_tensors: wrong number of tensors; expected 81, got 58 0
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:109958

### v1-#243 [env_fact, seen 1x in 1 session(s)]
- rewrite: 481:0.10.341.411 I slot process_sing: id 0 \| task -1 \| saving idle slot to prompt cache 483:0.10.341.586 I slot process_sing: id 1 \| task -1 \| saving idle slot to prompt cache 485:0.10.341.746 I slot process_sing: id 2 \|
- v1 text: 481:0.10.341.411 I slot process_sing: id 0 \| task -1 \| saving idle slot to prompt cache 483:0.10.341.586 I slot process_sing: id 1 \| task -1 \| saving idle slot to prompt cache 485:0.10.341.746 I slot process_sing: id 2 \|
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:111015

### v1-#248 [env_fact, seen 1x in 1 session(s)]
- rewrite: Okay, I just tried to just reproduce the compaction miss without changing anything.
- v1 text: Okay, I just tried to just reproduce the compaction miss without changing anything. I ran a turn or two and did lcm compact. The context was still small, and it didn't miss. Here are the pi and server logs. The pi log st
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:111825

### v1-#251 [env_fact, seen 1x in 1 session(s)]
- rewrite: So it sounds like you're proposing two patches.
- v1 text: So it sounds like you're proposing two patches. Are they two ways different ways of solving the same problem, or do they layer? Also, I assume the slots endpoint is reachable, but I did want to mention that I have been s
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:112132

### v1-#288 [env_fact, seen 1x in 1 session(s)]
- rewrite: Here's the current state of affairs in the office: Yes — the Macs are in the fleet, but not routing-eligible for any class The three Macs (cds-ai-a5404, cds-ai-a5407, cds-s24ma-5186 — the two M4 minis and the M2 Studio) 
- v1 text: Here's the current state of affairs in the office: Yes — the Macs are in the fleet, but not routing-eligible for any class The three Macs (cds-ai-a5404, cds-ai-a5407, cds-s24ma-5186 — the two M4 minis and the M2 Studio) 
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:118442

### v1-#291 [env_fact, seen 1x in 1 session(s)]
- rewrite: Is this wired into the gateway dashboard?
- v1 text: Is this wired into the gateway dashboard? It was running earlier. Here was its machine page at http://strix-halo.local:8090/fleet/machines
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:119396

### v1-#297 [env_fact, seen 1x in 1 session(s)]
- rewrite: Qwen speed tests: All boxes — 38k context, solo, warm ┌────────────┬─────────────────┬─────────────┬───────────┬──────────────────────────────────────┐ │ Box │ Type │ Prefill │ Decode │ Notes │ ├────────────┼────────────
- v1 text: Qwen speed tests: All boxes — 38k context, solo, warm ┌────────────┬─────────────────┬─────────────┬───────────┬──────────────────────────────────────┐ │ Box │ Type │ Prefill │ Decode │ Notes │ ├────────────┼────────────
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:120228

### v1-#300 [env_fact, seen 1x in 1 session(s)]
- rewrite: Okay, I am logged in now.
- v1 text: Okay, I am logged in now. Use nanobrowser to read: https://kaitchup.substack.com/p/qwen38-flash-next-review-benchmarks?utm_source=post-email-title&publication_id=1783977&post_id=212942986&utm_campaign=email-post-title&is
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:123538

### v1-#312 [convention, seen 1x in 1 session(s)]
- rewrite: Revision 2 is materially better.
- v1 text: Revision 2 is materially better. The measurements justify the pivot away from “continuous critic” toward context injection + structural enforcement + selective review. But I found two things I would change immediately—on
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:139169

### v1-#313 [env_fact, seen 1x in 1 session(s)]
- rewrite: Revision 2 is materially better.
- v1 text: Revision 2 is materially better. The measurements justify the pivot away from “continuous critic” toward context injection + structural enforcement + selective review. But I found two things I would change immediately—on
- sources: -var-home-bmosher/cf72207b-8cc8-4991-9026-7fbc2fd10d7a.jsonl:139169

### v1-#318 [env_fact, seen 1x in 1 session(s)]
- rewrite: /home/bmosher/.termrover/uploads/shot-1786670083180-1.png
- v1 text: /home/bmosher/.termrover/uploads/shot-1786670083180-1.png
- sources: -var-home-bmosher/f91a9ec1-7f20-4e5a-8ff6-388754d533a9.jsonl:71

## Probe corpus (probe → probe-corpus, invocation/outcome test material)

Full id list (v1 pointers; texts stay in the local digest, not repeated here):

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 20, 21, 24, 26, 27, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78, 81, 82, 85, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 103, 104, 113, 114, 116, 118, 122, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 135, 137, 139, 140, 142, 144, 145, 146, 147, 149, 150, 151, 153, 154, 155, 156, 157, 168, 172, 173, 175, 176, 177, 178, 179, 180, 181, 183, 184, 185, 188, 189, 190, 191, 192, 194, 197, 198, 204, 206, 207, 208, 209, 210, 212, 224, 227, 229, 235, 239, 240, 241, 242, 244, 245, 247, 249, 252, 254, 255, 258, 259, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 285, 287, 289, 292, 294, 295, 296, 298, 299, 303, 306, 308, 311, 315, 316

Dominant probe families: MLX/Qwen localhost:8088 curl + tool-call tests; cds-ai igw status curls; pi-start/[LCM] prewarm + slot launch/drift logs; ds4-server/ROCm logs; systemctl/memlock checks; agent-deck/conductor dispatches (MISSION/TEAM-1/RETRO-1/command scaffolding).

## Dropped (question + fuzzy, one-line why each)

- v1-#12 [fuzzy] I have been carrying on a long discussion with desktop Claude about this. Here it is: --- # Safety guardrails for Pi.dev coding assistant pilot **Created:** 8/7 — conversational/session-local framing — not a standalone fact.
- v1-#15 [fuzzy] Great. This proves out the Linux path nicely. One thing that I think we had discussed was the idea of setting a Pi hook to commit each turn to close the "edit t — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#18 [fuzzy] Okay, so a few things: 1. We audited the code for Pi 0.73.0 to make sure that there was no phone-home or privacy concerns, and we set PI_OFFLINE=1 in our startu — conversational/session-local framing — not a standalone fact.
- v1-#19 [fuzzy] Let's actually run the tests on the Mac, Windows, and Linux so we can fill out the table, and either show results or put Not Applicable. The Mac is still runnin — conversational/session-local framing — not a standalone fact.
- v1-#22 [fuzzy] So you're suggesting that my real Windows dev box should load pi from the real external @earendil-works/pi-coding-agent@0.84.4 npm rather than our registry? We  — conversational/session-local framing — not a standalone fact.
- v1-#23 [fuzzy] I backed up my current pi. Now I want to try installing a fresh dev instance. I'd like to use my coworker's install script, possibly slightly modified if necess — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#25 [fuzzy] $ node Downloads/whyasking.cjs agent dir : C:\Users\bmosher\.pi\agent config : C:\Users\bmosher\.pi\agent\extensions\pi-permission-system\config.json NOT PRESEN — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#28 [question] Can you tell me about the --security-opt label=disable and whether I should care? — open question, unresolvable as fact — parked.
- v1-#29 [fuzzy] The deploy script is running successfully. Great! One warning that seems harmless: /home/bmosher/.local/opt/hf-venv/lib64/python3.14/site-packages/huggingface_h — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#30 [fuzzy] Darn, our network proxy must have blocked something that was needed that we didn't check for:✓ Downloaded path: /var/home/bmosher/models/laguna-s-2.1/laguna-s-2 — hedged/second-hand claim — needs confidence or source.
- v1-#41 [fuzzy] === how files were modified === 460 non-writing 113 other write 13 regex sed 9 tool write 7 heredoc 2 literal sed recoverable by replay: 18 manual review needed — conversational/session-local framing — not a standalone fact.
- v1-#42 [fuzzy] Here is the output. I elided some sensitive strings. ====================================================================== READ CALL seq=1789 role=assistant to — conversational/session-local framing — not a standalone fact.
- v1-#45 [fuzzy] Okay, I think since it's mostly just the two files that are broken, I will have you fix them, since you're smart and will do a better job anyway and short circu — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#57 [fuzzy] I was just reading an article about qwen3.8-27b evals, and the comments there suggest that our greedy and temp=0 settings may be compromising our quality. I rea — hedged/second-hand claim — needs confidence or source.
- v1-#58 [fuzzy] The reason I mention it is that all the previous tool-eval-bench tests with the other models ran with the model card recommended settings. We are running temp=0 — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#74 [fuzzy] Wow, it sure thinks and thinks: I just switched to qwen3.6-27b to see how it works. Now, the problem at hand. We can't seem to get a detect, even in full daylig — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#79 [fuzzy] 0.00.014.444 W srv llama_server: ----------------- 0.00.014.446 W srv llama_server: CORS is set to allow all origins ('*') and no API key is set 0.00.014.447 W  — conversational/session-local framing — not a standalone fact.
- v1-#80 [fuzzy] Here's what my args look like before I reboot. ~$ rpm-ostree kargs ostree=/ostree/boot.0/fedora/f3eae5e57f386b8c75bce43e03c711e30223c38c5baaccf7f90f76621e2c8445 — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#83 [question] What's your thoughts on the amd_iommu=off ? — open question, unresolvable as fact — parked.
- v1-#84 [question] Shouldn't step 2 be trying to load our model normally first to see if iommu=off fixes it? — open question, unresolvable as fact — parked.
- v1-#86 [question] Which adapter extension is best? https://pi.dev/packages?name=headroom (nanobrowser). — open question, unresolvable as fact — parked.
- v1-#87 [fuzzy] Here's what I have: /var/home/bmosher/nathanw-v04/vulkan/llama-server --port ${PORT} -m /var/home/bmosher/models/thinkingcap-27b/ThinkingCap-Qwen3.6-27B-Q4_K_M. — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#100 [fuzzy] I was working in my session and the model said it was going to run a command, and then it didn't. It seemed to just stop, like it had answered my question and i — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#101 [fuzzy] Compaction fired with -np=1. Seemed quick, maybe a 3-4 seconds. 58.29.136.476 I slot print_timing: id 1 \| task 1762 \| n_decoded = 143, tg = 12.89 t/s, tg_3s = 1 — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#102 [fuzzy] I bumped the server down to 131072 and my models.json matches. I don't want to measure the eager summarization right now, maybe never. Here's the server log onc — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#105 [fuzzy] I think we decided that was a scoring criteria. — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#107 [fuzzy] Great. While we're waiting, check out my ChatGPT Deep Research report on eval harnesses. ---- # Repeatable Evaluation Systems for Local and Open-Weight LLM Codi — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#109 [fuzzy] Iommu=pt — fragment too short to stand as fact.
- v1-#111 [fuzzy] You're still using 127.0.0.1 which is mostly useless. — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#112 [fuzzy] Remember to do all this sort of preflight and dry run for Deepseek later, if you get that far. — instruction/reminder, not a durable fact.
- v1-#115 [fuzzy] You said my thinkingcap diverged but here is what I shared with you: /var/home/bmosher/nathanw-v04/vulkan/llama-server --port ${PORT} -m /var/home/bmosher/model — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#119 [fuzzy] If we have to run a thing on each server anyhow, maybe it should also be an auth gateway and point the servers at 127.0.0.1. — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#120 [question] Hold up (figuratively, don't stop it yet). Their machine is literally the same machine we have. The iommu=pt shouldn't make a difference in memory should it? — open question, unresolvable as fact — parked.
- v1-#121 [question] So we have been running our q2_q4 quant and I think we decided it was our best choice. Any reason to switch? — open question, unresolvable as fact — parked.
- v1-#138 [fuzzy] I reconciled my work config for qwen3.8-27b to the other entries, and here is what it has now. I also renamed it to match the others. # Qwen3.8-27B Q4_K_M. Pilo — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#141 [question] That brings up a good point. We are pinned at an older version of pi. For the rollout, we might want to bump to the latest. Can you review what's new compared t — open question, unresolvable as fact — parked.
- v1-#148 [fuzzy] Please package up the npu rollout as a single tarball. For good examples of preflight checks, see [~/deploy-thinkingcap-bosgame.sh](http://strix-halo.local:8888 — instruction/reminder, not a durable fact.
- v1-#158 [fuzzy] So here's something I am considering that I need you to weigh in on. Currently FLM doesn't have the same shape as llama-server regarding some of the auxiliary/m — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#160 [fuzzy] I had my models folder too far down and tried to move it up. I think I accidentally nuked it: $ ls -al /var/opt/ai/models/ total 0 drwxrwsr-x. 1 root ai 6 Aug 1 — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#165 [fuzzy] Okay, I found the culprit, but can't seem to kill it. I restarted you on the host so we can chat. Here is what I tried to run: sudo systemctl --user stop ClawdB — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#166 [fuzzy] Great. We're operational then. Back to its questions. I'll go through them one at a time. Overall it said it was happy with the repo, thought it was well-though — conversational/session-local framing — not a standalone fact.
- v1-#167 [fuzzy] " Done. Problem 1 is fixed, committed (79e5127), and pushed. What changed ┌─────────────────────────────────┬─────────────────────────────────────────────────── — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#169 [fuzzy] No no no. I want to see the diagram that we agreed on, and you explicitly showing where it was wrong. — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#170 [fuzzy] OH NO!!! Something has gone south on my work pi session and the prefill just keeps happening in a loop. "We gave it a spec and a bare directory — no starter cod — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#174 [fuzzy] Maybe something for #3, I saw these weird things happen in the session: $ [elided - recover with lcm_grep: query a kept value such as the path, or the tool name — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#182 [fuzzy] Something else weird now: 50.54.355.787 W slot operator(): id 2 \| task 1221 \| old: ... </tool_call><\|im_end\|> 50.54.355.789 W slot operator(): id 2 \| task 1221  — conversational/session-local framing — not a standalone fact.
- v1-#186 [fuzzy] I don't know if it makes any sense, but qwen was applying the TTL changes, and setting timers and generally doing surgery on itself right before, and it compact — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#187 [fuzzy] I don't know if it makes any sense, but qwen was applying the TTL changes, and setting timers and generally doing surgery on itself right before, and it compact — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#195 [question] I have been keeping our list separately because the chat scrolls away. Here's what I had. Tell me which items need strikethrough, and what's missing? Noted. Her — open question, unresolvable as fact — parked.
- v1-#196 [fuzzy] Okay, this is a real unexplained prefill. I typed a short prompt and got * working for no known reason: 310.10.713.054 W slot operator(): id 3 \| task 9663 \| new — conversational/session-local framing — not a standalone fact.
- v1-#199 [fuzzy] Meanwhile, here is what qwen is working on: " Confirmed the exact post-compaction state. Both my pre-compaction port fixes are in place: - router.json: all thre — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#201 [fuzzy] === 1. did llama-swap restart? === ActiveEnterTimestamp= NRestarts=0 ExecMainStartTimestamp= === 2. is -watch-config set? (it kills loaded models on ANY config  — conversational/session-local framing — not a standalone fact.
- v1-#202 [fuzzy] Here. I reran it as svc: === 1. did llama-swap restart? === ActiveEnterTimestamp=Fri 2026-08-21 16:29:12 PDT NRestarts=1 ExecMainStartTimestamp=Fri 2026-08-21 1 — conversational/session-local framing — not a standalone fact.
- v1-#203 [question] === was a model being loaded when it died? === === what is using 78GB right now === RSS USER COMMAND 7563728 svc-cdsbb-aa /opt/fastflowlm/bin/flm serve qwen3-it — open question, unresolvable as fact — parked.
- v1-#205 [fuzzy] Okay. A couple of problems solved! Here's where qwen left off: --- Here's the NPU situation, clean and current, for Claude: NPU-through-gateway: blocked on a de — conversational/session-local framing — not a standalone fact.
- v1-#213 [fuzzy] ChatGPT: --- Yes. I think there is a real error in the analysis, and it changes the direction of the investigation substantially. The key error: exclusion #1 is — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#214 [fuzzy] ChatGPT: Yes — this resolves the original mystery cleanly, and the evidence is much stronger than the earlier inferential model. The key result is not merely th — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#215 [fuzzy] This is now a genuinely convincing root-cause analysis. The pipeline statistics close the last major inferential gap: you have an end-to-end curve, op attributi — conversational/session-local framing — not a standalone fact.
- v1-#217 [fuzzy] Yes. The investigation is resolved now, but the document itself still needs one editorial pass because the main body contains statements that the later addenda  — conversational/session-local framing — not a standalone fact.
- v1-#218 [question] So the model card suggests temp=1.0, doesn't it. What are the pros and cons of setting it to near zero? — open question, unresolvable as fact — parked.
- v1-#219 [question] We are already setting GGML_VK_FORCE_MMVQ=1 , aren't we? — open question, unresolvable as fact — parked.
- v1-#220 [question] What is the overall speed improvement for the day, beginning this morning to now with this at temp=0? — open question, unresolvable as fact — parked.
- v1-#221 [fuzzy] ChatGPT: --- I think Claude’s latest is materially better, but PART 1 still has a very plausible “fourth wall” that they have not tested: test-backend-ops is me — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#222 [fuzzy] I sent your earlier retraction already. ChatGPT said this: --- This is actually an excellent ending to the weekend, even if it is painful. The retraction is cle — conversational/session-local framing — not a standalone fact.
- v1-#223 [fuzzy] ChatGPT's take on it: --- Claude has the right instinct to reopen the accounting, but I think the 26% figure is not yet a valid “unaccounted overhead” number. I — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#225 [fuzzy] Well, here is his feedback. You can react and save memories, but then we are switching gears to the ig. --- This is a very productive morning. I think Claude ha — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#226 [fuzzy] I asked qwen about the affinity ttl: Here's the complete answer. The affinity TTL change (1800 → 14400) was made in one file, in two places: Where the change li — conversational/session-local framing — not a standalone fact.
- v1-#230 [fuzzy] Qwen reports: --- Where things stand Deploy complete and verified working (PID 1192461): - ✅ Affinity persistence is live (--state-file in the running process,  — conversational/session-local framing — not a standalone fact.
- v1-#231 [fuzzy] Qwen status report: --- Fully verified — and the persistence is provably working. The affinity.json (which survived the restart) contains 2 live pins, both on c — conversational/session-local framing — not a standalone fact.
- v1-#232 [fuzzy] While we're at it, I had ChatGPT review and write a version of the affinity doc. --- # Affinity: how the gateway keeps conversations on the right machine Affini — conversational/session-local framing — not a standalone fact.
- v1-#234 [question] Actually, before I end for the day, I want to roll out our model speed up work from this weekend. (Remember that?). Here is a deploy doc you wrote, can you see  — open question, unresolvable as fact — parked.
- v1-#237 [question] Hmm, so I manually ran lcm compact and it paused for a while after the compaction like it was prefilling, but I don't see it in the log, and it seems like I got — open question, unresolvable as fact — parked.
- v1-#238 [question] Do you just want the beginning of the server log? Here it is: 0.00.040.961 I cmn common_param: common_params_print_info: verbosity = 3 (adjust with the `-lv N`  — open question, unresolvable as fact — parked.
- v1-#246 [fuzzy] Here is the pi.log: ===== pi start 2026-08-24 12:42:27 ===== [LCM] OK pre-loading the 36 tool(s) Pi sends (39 are registered; switched off and correctly left ou — conversational/session-local framing — not a standalone fact.
- v1-#250 [fuzzy] 5806 directly: 663.19.323.563 I srv update_slots: all slots are idle 663.26.766.256 I srv update_slots: all slots are idle 663.35.318.103 I srv update_slots: al — conversational/session-local framing — not a standalone fact.
- v1-#253 [fuzzy] Hmm, everything deployed and restarted, and the tests pass, but the pi.log still says this: ===== pi start 2026-08-25 12:11:12 ===== [LCM] OK pre-loading the 36 — conversational/session-local framing — not a standalone fact.
- v1-#256 [fuzzy] I think it worked. Here is the pi.log and I put a -> marker at the spot where I ran compaction ===== pi start 2026-08-25 12:40:54 ===== [LCM] OK pre-loading the — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#257 [fuzzy] Well, something didn't work quite right. I waited like you said. Pi.log at compaction -> [LCM] compaction context 37,279 tok (threshold 131,072) [LCM] summarise — conversational/session-local framing — not a standalone fact.
- v1-#260 [fuzzy] Well, it completed. Here are the pi and server logs. ===== pi start 2026-08-25 13:06:00 ===== [LCM] OK pre-loading the 36 tool(s) Pi sends (39 are registered; s — conversational/session-local framing — not a standalone fact.
- v1-#261 [fuzzy] I think it still was too short. ===== pi start 2026-08-25 14:20:05 ===== [LCM] OK pre-loading the 36 tool(s) Pi sends (39 are registered; switched off and corre — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#284 [fuzzy] Great. Now some pi-lcm compaction. [LCM] OK pre-loading the 36 tool(s) Pi sends (39 are registered; switched off and correctly left out: grep, find, ls)xt for m — conversational/session-local framing — not a standalone fact.
- v1-#286 [question] If Alice arrives and gets pinned to the same box as Bob who went away, does Bob's reserved conversation impact Alice's responsiveness? — open question, unresolvable as fact — parked.
- v1-#290 [fuzzy] From qwen: --- Deployed and verified. Here's where things stand. 3be6bd0 deployed — a5407 is now in the rotation - Box at 3be6bd0, gateway active, selftest PASS — conversational/session-local framing — not a standalone fact.
- v1-#293 [fuzzy] Here are qwen's mac test results: ---- a5407 (serial Mac) — measured ┌─────────────────┬─────────────────────┬──────────────────────┬──────────────────────┐ │ M — conversational/session-local framing — not a standalone fact.
- v1-#301 [question] We are about to bring up caddy. We aren't ready to disconnect the backends (:8080 (linux) and :8088 (macs))from 0.0.0.0 yet. We want to get caddy working before — open question, unresolvable as fact — parked.
- v1-#302 [question] We are about to bring up caddy. We aren't ready to disconnect the backends (:8080 (linux) and :8088 (macs))from 0.0.0.0 yet. We want to get caddy working before — open question, unresolvable as fact — parked.
- v1-#304 [fuzzy] qwen is wiring up the gateway -> poller files through caddy. Here is where it's at: --- Now I have the complete diagnosis. Let me summarize what I found: Diagno — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#305 [fuzzy] From qwen: --- Flow B is now wired end-to-end (for the 6 physical boxes) What was the gap: The §30 "each box publishes, the gateway pulls" transport was built b — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#307 [fuzzy] From qwen: --- Done. Here's the complete picture. Option (b) implemented and verified The fix (commit faa4c06, deployed to a5410): - igw/poller/__main__.py: new — conversational/session-local framing — not a standalone fact.
- v1-#309 [fuzzy] While that runs, we are trying to come up with Pi guardrails for our work team. Fable had these recommendations: --- Here's the whole thing, boiled down. Everyo — conversational/session-local framing — not a standalone fact.
- v1-#310 [fuzzy] Here is ChatGPT's take on our idea. --- Yes. I think the right architecture is two deliberately asymmetric loops sharing one knowledge layer, not one general-pu — hedged/uncertain claim — needs confidence, not vault-ready.
- v1-#314 [fuzzy] It got Exit code 7 EXIT=0 http_code=000 — fragment too short to stand as fact.
- v1-#317 [fuzzy] Yes, just tackle the general infra problem, but i have been researching and i think I'd like to try the most popular off-the-shelf solution for this, Claude-Mem — hedged/uncertain claim — needs confidence, not vault-ready.

## Evidence the classifier bit: 5 strangest question rows

- v1-#203: === was a model being loaded when it died? === === what is using 78GB right now === RSS USER COMMAND 7563728 svc-cdsbb-aa /opt/fastflowlm/bin/flm serve qwen3-it:4b --host 0.0.0.0 --port 52626 140020 s
- v1-#195: I have been keeping our list separately because the chat scrolls away. Here's what I had. Tell me which items need strikethrough, and what's missing? Noted. Here's the list. ## Tomorrow morning - ~~**
- v1-#286: If Alice arrives and gets pinned to the same box as Bob who went away, does Bob's reserved conversation impact Alice's responsiveness?
- v1-#237: Hmm, so I manually ran lcm compact and it paused for a while after the compaction like it was prefilling, but I don't see it in the log, and it seems like I got moved to a different slot. What was goi
- v1-#120: Hold up (figuratively, don't stop it yet). Their machine is literally the same machine we have. The iommu=pt shouldn't make a difference in memory should it?
