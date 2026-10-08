# Foundry Guide demo — narration script

Scene-by-scene narration for the narrated demo video. Each `## <scene-id>` heading starts a scene; the paragraph(s)
below it are spoken by Azure AI Speech (`en-US-AndrewMultilingualNeural`). Scene ids must match the scene functions in
`capture.py`. HTML comments are ignored by the parser and describe what is on screen.

Prompts are the ones from `docs/session/demo-runbook.md` (Demo 1, steps 1, 2, 3, 5 and 6) so the video can stand in
for the live demo. Prices are illustrative, not list prices.

## title

<!-- Title card: "Microsoft Foundry — From prompt to production agent". -->

Microsoft Foundry: from prompt to production agent. In the next few minutes, we'll walk through Foundry Guide, a
small web app running on Azure Container Apps and backed by a prompt agent in Microsoft Foundry Agent Service. You'll
see grounded answers, real code execution, a side-by-side model comparison, and run history. And all of it is
keyless.

## about

<!-- About tab: architecture timeline on the left, live deployment details from /api/info on the right. -->

Let's start with the architecture. A Vue front end and a FastAPI back end run in a single container on Azure
Container Apps. The back end calls our Foundry project with a user-assigned managed identity. There are no API keys
anywhere, and local authentication is disabled on the Foundry resource. On the right are the live deployment details:
the project runs in Sweden Central, with gpt-5.4-mini as the agent model and gpt-5.4-nano
as the fast model. The foundry-guide agent has two tools: the Microsoft Learn MCP server, and Code Interpreter.
Traces flow to Application Insights through OpenTelemetry.

## agent-ask

<!-- Agent chat tab: type the runbook step 2 prompt, send, the thinking indicator runs while MCP is called. -->

Now, the agent. I'll ask a question that needs current documentation: what is the difference between prompt agents
and hosted agents in Foundry Agent Service, with Microsoft Learn citations. The agent decides on its own to call the
Microsoft Learn MCP server. That server is public, read-only, and needs no credentials, so we let the agent call it
without approval. For any tool that writes data, keep approvals on.

## agent-answer

<!-- Scroll through the answer: MCP tool-call chips at the top, Learn links, latency and token footer. -->

Here's the answer. Prompt agents combine instructions, a model, and tools, fully managed by Foundry. Hosted agents
run your own code and framework in a managed container. Look at the chips at the top: these are the MCP calls the
agent made. And the links point back to learn.microsoft.com. Grounded, not guessed. Underneath, you can see the
latency and the token usage for this turn.

## ci-ask

<!-- Same conversation: type the runbook step 3 Code Interpreter prompt and send. -->

Next, numbers. Language models are unreliable at arithmetic, so the agent's instructions say: use Code Interpreter for
any calculation. I'm asking for the cost of two thousand conversations a day, each with fifteen hundred input tokens
and five hundred output tokens, at illustrative prices of forty cents per million input tokens and one dollar sixty
per million output tokens. These are not list prices, so always check the Azure pricing page. The agent now writes
Python and runs it in a sandbox.

## ci-answer

<!-- Scroll through the Code Interpreter answer: chip, cost table, and the generated bar chart. -->

And here is the result, computed rather than guessed: two dollars and eighty cents per day, eighty-four dollars over
thirty days, and one thousand and twenty-two dollars over a year. The Code Interpreter chip shows the tool that ran,
and the bar chart is an image generated in the sandbox and served back through the app. This is the same conversation
as before: Foundry keeps the conversation state on the server side.

## compare-ask

<!-- Model compare tab: type the runbook step 5 prompt and click Compare; skeleton loaders while both models run. -->

Which model should power an agent like this? Let's measure. On the Model compare tab, the same prompt goes to two
Foundry deployments in parallel through the Responses API: gpt-5.4-mini, and gpt-5.4-nano.
The prompt: in three bullets, explain why teams put an AI gateway in front of their models.

## compare-result

<!-- Two result cards side by side with latency, input, output and total token chips; the fastest gets a trophy. -->

Two answers, side by side, each with its latency and its input and output tokens, and a trophy for the fastest
response. For many tasks, the smaller model is good enough. The only way to know is to measure, ideally with
evaluations.

## history

<!-- Run history tab: sort by latency, search for "compare", clear the search. -->

Every call we just made lands in Run history: the time, the kind of run, the agent or model, latency, tokens, tool
calls, and status. I can sort by latency, or search for just the model comparisons. It's kept in memory for the demo.
In production, the same signals live in Application Insights as OpenTelemetry traces.

## closing

<!-- About tab again. -->

To recap: a prompt agent in Microsoft Foundry Agent Service, grounded in Microsoft Learn through MCP, doing real math
in Code Interpreter, called keylessly from Azure Container Apps, with every run traced. The source code, the Bicep
infrastructure, and the GitHub Actions pipeline are all in the repository linked on the About page. Thanks for
watching.
