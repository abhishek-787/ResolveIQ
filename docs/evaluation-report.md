# ResolveIQ Evaluation Report

ResolveIQ was evaluated against a fixed 8-case ShopEase benchmark covering routing, tool selection, retrieval sufficiency, resolution planning, guardrails, citation behavior, reliability, and latency.

## Results

| Metric | Result |
|---|---:|
| Benchmark Cases | 8 |
| Passed Cases | 8 / 8 |
| Overall Pass Rate | 100% |
| Route Accuracy | 100% |
| Required Tool Selection Accuracy | 100% |
| Knowledge Sufficiency Accuracy | 100% |
| Resolution Accuracy | 100% |
| Guardrail Accuracy | 100% |
| Citation Compliance | 100% |
| Error-Free Rate | 100% |
| Average Latency | 9.23 s |
| Median Latency | 7.46 s |

## Benchmark Coverage

The benchmark includes cases covering:

- Standard return-policy questions
- Damaged-product evidence requirements
- Structured order lookups
- Wrong-product support
- Refund timing
- Missing delivery-policy evidence
- Product troubleshooting with insufficient knowledge
- Damaged-product replacement scenarios

Evaluation runs are also persisted through ResolveIQ's observability layer for later inspection.

> Results apply to the fixed 8-case ShopEase benchmark and should not be interpreted as universal production accuracy.