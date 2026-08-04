# LLM Chat CLI

A simple Python command-line application for chatting with an LLM through an
OpenAI-compatible API.

## Current features

- Interactive conversations directly in the terminal
- Conversation history preserved during the current session
- Configurable API key, base URL, and model name through environment variables
- A custom system rule entered by the user when each session starts
- User-configurable `max_tokens`, `temperature`, and `top_p` for each session
- Low-effort reasoning configuration for compatible providers
- Total token usage displayed when the API returns usage information
- A warning when a response stops because it reached the token limit
- Friendly messages for configuration, API, and empty-response errors
- `exit` and `quit` commands for ending the conversation

## Requirements

- Python 3.10 or newer
- An API key for an OpenAI-compatible LLM provider

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/Miladkhoshdel/llm-chat-cli
cd llm-chat-cli
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

Then add your provider credentials to `.env`:

```env
API_KEY=your_api_key
BASE_URL=https://your-provider.example/v1
MODEL_NAME=your_model_name
```

The `.env` file is ignored by Git, so credentials are not committed to the
repository.

`MODEL_NAME` must match a model identifier supported by your provider.

## Interactive session settings

The following values are requested in the terminal each time the application
starts; they are not read from `.env`:

- **System rule:** Instructions that define the assistant's role and behavior
- **Max tokens:** A positive integer that limits the generated response
- **Temperature:** A number from `0` to `2`; lower values are more predictable
- **Top-p:** A number from `0` to `1` that controls token sampling

## Usage

Run the application:

```bash
python3 main.py
```

Example:

```text
System rule: You are a concise Python programming teacher.
Max tokens: 500
Temperature (0-2): 0.1
Top-p (0-1): 0.9
You: Explain a Python list in one sentence.
Assistant: A Python list is an ordered, mutable collection of values.
```

Continue entering messages at the `You:` prompt. Type `exit` or `quit` to close
the application. Invalid or empty settings are rejected and requested again.

## Current limitations

- Conversation history is stored only in memory and is lost when the program
  exits.
- The system rule must be entered again when a new session starts.
- Generation settings must be entered again when a new session starts.
- The reasoning configuration may not be supported by every OpenAI-compatible
  provider.

## Security

Never commit your `.env` file or API key. If a credential is exposed, revoke it
through your provider and create a replacement.
