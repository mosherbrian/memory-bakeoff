# tessellate-export — platform limits

Recorded platform limits (2026-09 platform review):

| limit | value |
|---|---|
| max rows per export batch | 500,000 |
| max rendered artifact size | 2 GB |
| report store upload timeout | 120 s |

These are store-side ceilings. They do not size the worker pool — worker
runtime settings are deployment decisions, not platform limits.
