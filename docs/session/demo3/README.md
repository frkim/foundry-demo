# Demo 3 assets

Small, public, fictional assets used by [Demo 3 in the demo runbook](../demo-runbook.md#demo-3--foundry-capabilities-ten-short-demos).
Zava is a fictional retailer (the same one used in [frkim/apim-demo](https://github.com/frkim/apim-demo)); nothing here
is real customer data.

| File | Used by | Purpose |
| --- | --- | --- |
| [`knowledge/zava-returns-policy.md`](knowledge/zava-returns-policy.md) | 3.1 Foundry IQ | Knowledge source document |
| [`knowledge/zava-shipping-faq.md`](knowledge/zava-shipping-faq.md) | 3.1 Foundry IQ | Knowledge source document |
| [`knowledge/zava-supplier-notes.md`](knowledge/zava-supplier-notes.md) | 3.4 Guardrails | Contains a **deliberate indirect prompt injection** (see the HTML comment) to trigger the tool-response guardrail |
| [`eval-queries.jsonl`](eval-queries.jsonl) | 3.8 Evaluation | Ten test queries for the `foundry-guide` agent |
| [`skills/foundry-cost-estimate/SKILL.md`](skills/foundry-cost-estimate/SKILL.md) | 3.5 Skills | A reusable skill: token-cost estimates with Code Interpreter |

> Keep `zava-supplier-notes.md` out of any knowledge base that real users can reach — it exists only to demonstrate
> prompt-injection defenses.
