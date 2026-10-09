---
name: foundry-cost-estimate
description: Estimate model token costs for an AI workload with Code Interpreter and present them as a table and a chart.
---

# Foundry cost estimate

Use this skill when the user asks how much a model or agent workload costs.

1. Collect the inputs: requests per day, input tokens and output tokens per request, and the price per 1M input and
   output tokens. If a price is missing, ask for it — never invent list prices.
2. Use **Code Interpreter** for every calculation. Compute the daily, 30-day and 365-day cost, split into input and
   output.
3. Answer with a Markdown table (period, input tokens, output tokens, cost) and a bar chart saved as a PNG file.
4. State that the prices are the user's inputs and that the Azure pricing page is the source of truth.
