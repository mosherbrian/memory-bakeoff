# Grounded refresh: a useful contrast, not a robotics recommendation

Tern ·26 September2026 · cycle34 initial source reading; panel synthesis pending.

[DynaMem v1](https://arxiv.org/html/2411.04999v1), §§3–5: a voxel memory stores semantic features, image references and observation times. New depth observations can invalidate occupied voxels through ray-casting; navigation repeatedly scans and replans. Query candidates are checked by an object detector, allowing not-found responses. Images with no remaining voxel reference are removed from the query context; this is not a lossless historical-store claim.

The lab comparison reports 70% versus30% pick-and-drop success on30 queries against static OK-Robot, with exploration/navigation differences as well as memory. Offline DynaBench separately tests localization: default70.6%, add-only67.8%, without detector cross-check59.2%. Home trials succeed9/17. Neither supplies evidence about remembered software procedures or preferences.

**Inference, medium confidence:** refresh a current state model using observations capable of contradicting it. This is more informative than merely choosing the newest remembered sentence. The observation model determines what can be invalidated; an unseen change remains possible. For Brian, current files/configs/logs are analogous evidence sources, but designing an appropriate check still costs work and does not certify an entire procedure. Borrow the distinction, not the robot stack. High confidence in source scope; transfer unmeasured.
