# LLM Code Review CLI

A Python command-line code-review assistant that runs Flake8 against a project
and uses an LLM through an OpenAI-compatible API to explain and prioritize the
findings. The project also includes an interactive, streaming chat interface.

## Features

- Streamed responses displayed as soon as chunks arrive
- A configurable number of recent exchanges preserved during the current session
- API, model, generation, and usage settings configured through `.env`
- A custom system rule entered by the user when each session starts
- Low-effort reasoning configuration for compatible providers
- Optional prompt, completion, reasoning, total-token, and cost reporting
- A warning when a response stops because it reached the token limit
- Flake8-based directory reviews explained in human-readable language by the LLM
- Graceful configuration and API error handling
- `exit` and `quit` commands for ending the conversation

## Requirements

- Python 3.10 or newer
- An API key for an OpenAI-compatible LLM provider
- Flake8, installed through `requirements.txt`

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/Miladkhoshdel/llm-code-review-cli
cd llm-code-review-cli
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then configure `.env` for your API provider:

```env
API_KEY=your_api_key
BASE_URL=https://your-provider.example/v1
MODEL_NAME=your_model_name
SHOW_USAGE=true
MAX_TOKENS=1000
TEMPERATURE=0.2
TOP_P=1.0
MEMORY_KEEP_COUNT=10
```

The `.env` file is ignored by Git, so credentials are not committed to the
repository.

All variables are currently required. `MODEL_NAME` must be an exact model ID
supported by the configured provider.

## Environment variable reference

| Variable | Type | Valid value | Recommended starting value | Purpose |
| --- | --- | --- | --- | --- |
| `API_KEY` | String | Non-empty provider API key | Your secret key | Authenticates API requests |
| `BASE_URL` | String | Valid compatible API base URL | Your provider's API URL | Selects the API endpoint |
| `MODEL_NAME` | String | Exact provider model ID | A supported model ID | Selects the model |
| `SHOW_USAGE` | Boolean | `true` or `false` | `true` | Shows usage after each response |
| `MAX_TOKENS` | Integer | `1` or greater | `1000` | Limits completion tokens per response |
| `TEMPERATURE` | Number | `0` through `2` | `0.2` or `0.7` | Controls randomness |
| `TOP_P` | Number | `0` through `1` | `1.0` | Limits sampling to likely tokens |
| `MEMORY_KEEP_COUNT` | Integer | `0` or greater | `10` | Keeps this many completed exchanges in conversation history |

Providers and individual models may enforce narrower limits than the ranges
above. Invalid values are rejected either during configuration parsing or by
the API provider.

### Choosing `MAX_TOKENS`

`MAX_TOKENS` limits the output token budget; it does not represent a number of
words. For reasoning models, reasoning tokens can consume part of this budget.

- `200` to `500`: concise answers and simple chat
- `500` to `1000`: a useful general-purpose range
- `1000` to `4000`: detailed explanations or longer generated content

Larger values do not force the model to produce a long answer. They only allow
it to produce up to that limit. A request can still stop earlier with
`finish_reason="stop"`. If it stops with `finish_reason="length"`, increase
`MAX_TOKENS` or request a shorter response.

### Choosing `TEMPERATURE`

Temperature changes how strongly the model favors its most likely next token.

- `0` to `0.2`: extraction, classification, factual answers, and predictable output
- `0.5` to `0.7`: balanced general conversation
- `0.8` to `1.2`: brainstorming and creative writing
- Above `1.2`: increasingly unpredictable; rarely needed

Even `TEMPERATURE=0` does not guarantee identical output on every request.

### Choosing `TOP_P`

Top-p removes low-probability token choices until the remaining candidates
reach the configured cumulative probability.

- `1.0`: keep the full candidate distribution; recommended when adjusting temperature
- `0.9` to `0.95`: slightly restrict unlikely choices
- Below `0.8`: strongly restricted output that may become repetitive

Although the API allows temperature and top-p to be changed together, it is
easier to tune one control at a time. A good default is:

```env
TEMPERATURE=0.7
TOP_P=1.0
```

### Suggested presets

Predictable technical assistant:

```env
MAX_TOKENS=1000
TEMPERATURE=0.2
TOP_P=1.0
```

Balanced general chatbot:

```env
MAX_TOKENS=1000
TEMPERATURE=0.7
TOP_P=1.0
```

Creative assistant:

```env
MAX_TOKENS=1500
TEMPERATURE=1.0
TOP_P=1.0
```

## Provider compatibility

The current implementation is compatible with OpenRouter, including streaming,
usage reporting, and its configured reasoning options. Other providers may
require some of the adaptations described below.

"OpenAI-compatible" does not mean that every provider supports every request
parameter or response field. Compatibility is often limited to the basic
Chat Completions request and response structure. Model capabilities can also
differ within the same provider.

The following parts of this application may require changes when switching
providers or models:

| Parameter or field | Possible incompatibility | What to check or change |
| --- | --- | --- |
| `BASE_URL` | Every provider uses its own endpoint | Set the exact API base URL supplied by the provider |
| `MODEL_NAME` | Model identifiers are provider-specific | Use an exact model ID listed by the provider |
| Chat Completions | Some APIs support another response endpoint instead, or implement Chat Completions only partially | Confirm that the provider supports streamed Chat Completions |
| `max_tokens` | Some models use `max_completion_tokens` instead; reasoning models may reject `max_tokens` | Rename the request argument when required by the selected API/model |
| `temperature` | Some reasoning models reject or ignore sampling controls | Omit it when the selected model does not support it |
| `top_p` | Some reasoning models reject or ignore sampling controls | Omit it when the selected model does not support it |
| `extra_body.reasoning` | Reasoning configuration is not standardized across providers | Remove it, rename it, or use the provider's supported reasoning parameter |
| `reasoning.effort` | Supported effort names and levels differ by model | Check whether values such as `low` are supported |
| `reasoning.exclude` | Some providers never return reasoning text; others use a different option | Remove this field if it is unsupported |
| `stream_options.include_usage` | Some providers stream text but do not send a final usage chunk | Allow `usage` to remain `None` |
| `usage.completion_tokens_details.reasoning_tokens` | Reasoning-token details are optional | Check for `None` before accessing nested fields |
| `usage.cost` | Cost is not part of every compatible usage object | Treat missing cost as normal or calculate it separately |
| `finish_reason` | Providers may return different finish-reason values | Handle unknown values without crashing |

The current implementation is most likely to need changes in these two places:

```python
max_tokens=max_tokens
```

Some APIs and models require:

```python
max_completion_tokens=max_tokens
```

The reasoning object is also provider-dependent:

```python
extra_body={
    "reasoning": {
        "effort": "low",
        "exclude": True,
    }
}
```

If a provider rejects an unknown parameter, remove that parameter or replace it
with the provider's documented equivalent. Do not assume that changing only
`BASE_URL` and `MODEL_NAME` guarantees full compatibility.

Before switching providers:

1. Confirm support for the Chat Completions endpoint and streaming.
2. Set the provider's exact base URL and model ID.
3. Verify the supported token-limit and reasoning parameters.
4. Check whether the selected model supports temperature and top-p.
5. Send one small test request and inspect its chunks, finish reason, and usage.

## Streaming

Streaming is always enabled. Instead of waiting for a complete response, the
application processes and prints each content chunk as it arrives. The chunks
are collected and joined into a complete assistant message before that message
is added to conversation history.

Streaming improves perceived responsiveness, but it does not reduce token
usage, reasoning, cost, or necessarily the total generation time. The stream
closes automatically after normal completion or an exception.

When `SHOW_USAGE=true`, the application requests usage information in the
stream and displays it after generation. Some compatible providers may not
return every provider-specific field, such as reasoning tokens or cost.

## Conversation memory

`MEMORY_KEEP_COUNT` controls how many completed user/assistant exchanges are
sent with the next request. The system rule is always retained. For example,
`MEMORY_KEEP_COUNT=10` keeps the latest ten exchanges and removes older ones
after each successful response.

Set `MEMORY_KEEP_COUNT=0` to keep only the system rule between prompts. This
makes each new prompt independent of earlier prompts in the same session.

## System rule

The system rule is the only setting requested when the program starts. It
defines the assistant's role and behavior for the entire conversation:

```text
System rule: You are a concise Python programming teacher.
```

Empty system rules are rejected.

## Usage

Run the application:

```bash
python3 main.py
```

Example:

```text
System rule: You are a concise Python programming teacher.

You: Explain a Python list in one sentence.
A Python list is an ordered, mutable collection of values.
-----
Prompt tokens: 24
Completion tokens: 15
Total tokens: 39
Reasoning tokens: 0
Cost: 0
-----
```

Continue entering messages at the `You:` prompt. Type `exit` or `quit` to close
the application.

## Code review

Run a review against a Python project directory:

```bash
python3 review.py path/to/project
```

If the directory is omitted, the current directory is reviewed. The command
runs Flake8 locally, converts its output into structured findings, and sends the
finding details and affected source lines to the configured LLM. The resulting
report uses a compact, terminal-friendly plain-text format, lists likely bugs
before style and maintainability issues, and includes a suggested fix for each
kind of finding. Repeated findings are grouped with a count and up to three
example locations instead of being expanded into a Markdown table or a long
list of paths. The report is printed as the LLM generates it.

When Flake8 finds no issues, the command prints `No Flake8 findings.` and does
not call the LLM. Existing Flake8 configuration in the reviewed project is
respected. Virtual-environment directories named `.venv` or `venv` are excluded.

## Troubleshooting

### Configuration error

Confirm every required variable exists in `.env`, has no surrounding quotes
unless they are part of the value, and uses a valid type. In particular:

```env
SHOW_USAGE=true
MAX_TOKENS=1000
TEMPERATURE=0.7
TOP_P=1.0
MEMORY_KEEP_COUNT=10
```

### Usage information is not displayed

Set `SHOW_USAGE=true`. Usage is delivered near the end of the stream, and some
OpenAI-compatible providers may omit it or omit provider-specific fields.

### Response is incomplete

If the program reports that the finish reason was `length`, increase
`MAX_TOKENS` or ask for a shorter response. Reasoning models may use a portion
of the completion budget before producing visible text.

### Rate-limit or provider error

Wait before retrying a rate-limited request, reduce request frequency, or use a
different available model/provider. Free model availability can fluctuate.

## Current limitations

- Conversation history is stored only in memory and is lost when the program
  exits.
- Old conversation exchanges are removed rather than summarized when the
  configured memory limit is reached.
- The system rule must be entered again when a new session starts.
- The reasoning configuration may not be supported by every OpenAI-compatible
  provider.

## Security

Never commit your `.env` file or API key. If a credential is exposed, revoke it
through your provider and create a replacement.

The code-review command sends Flake8 findings and the affected source lines to
the configured LLM provider. Do not use it on code that must remain entirely
local unless the provider is approved to receive that code.
