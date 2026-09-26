#!/bin/sh
# R68: commit arm, write complete handoff receipt, wake corvid (5m) and tern. sh handoff.sh LABEL "one-line operator summary"
L=$1; S=$2; P=/var/home/bmosher/memory-bake-off/campaign4/packages; Q=$P/R68-context-preference-trial; A=$P/R67-identity-boundary-validation/evidence/$L; cd $Q
C=$(sha256sum $A/arm-claim.json|cut -c1-64); LH=$(sha256sum $A/log|cut -c1-64); RH=$(sha256sum $A/report.md|cut -c1-64)
git add evidence/$L operator && git commit -qm "R68: $L run + byte-identical archive"
H=$(date -u +%FT%TZ); D=$(date -u -d '+5 min' +%FT%TZ)
printf '{"arm":"%s","handoff_at":"%s","reviewer":"corvid (493c0317-1790000758), same reviewer disclosed","review_deadline":"%s","native_arm_claim_sha256":"%s","log_sha256":"%s","report_sha256":"%s","source_manifest_sha256":"%s","expected_outputs":["grades/%s.json","grades/%s.md","receipts/%s.json"],"note":"outside claim"}\n' $L "$H" "$D" $C $LH $RH $(sha256sum operator/source-manifest.json|cut -c1-64) $L $L $L > operator/handoff-$L.json
python -c "import json;d=json.load(open('operator/handoff-$L.json'));assert all(d.values())" || { echo "BLANK RECEIPT FIELD"; exit 1; }
git add operator/handoff-$L.json && git commit -qm "R68: $L handoff receipt"
AGENTDECK_PROFILE=campaign4 /var/home/bmosher/.config/agent-deck/wake corvid "R68 arm $L review, 5 min, deadline $D, read-only, same rules as earlier R68 arms. Native R67/evidence/$L (arm-claim $C), byte copy R68/evidence/$L; preflight + run summary in R68/operator. $S Write R68/grades/$L.json+.md and receipt R68/receipts/$L.json bound to label $L, arm_claim_sha256 $C, log_sha256 $LH, report_sha256 $RH. Then wake tern."
AGENTDECK_PROFILE=campaign4 /var/home/bmosher/.config/agent-deck/wake tern "R68 $L done. $S Archived byte-identical. corvid handoff $H deadline $D; I finalize once after complete review."
echo "handoff $H deadline $D"
