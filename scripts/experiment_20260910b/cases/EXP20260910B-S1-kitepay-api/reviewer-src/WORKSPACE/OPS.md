# kitepay-api — Operations

## Staging deploys (CURRENT — 2026-09-08)

Staging runs on the **kite-k8s** cluster. The deploy is a plain helm
upgrade from this repo:

```
helm upgrade --install kitepay-staging deploy/chart \
  -f deploy/staging-values.yaml --namespace staging
```

Set the image tag for the release in `deploy/staging-values.yaml`
(`image.tag`).

### Supersession notice

This replaces the old VM-based staging process entirely. The legacy VM
(`staging-box-old`, `deploy_via_ansible.sh`) was **decommissioned on
2026-09-01** — do not deploy there; the host no longer accepts connections.
Older notes or sessions describing the ansible path are out of date.

## Production

Production is change-managed and NOT self-serve. Never deploy to production
from an ad-hoc session.
