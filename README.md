# typesafe-jev

A minimal Python client for TypeSafe's **Jev** model, served through OpenRouter's Decisions API.

Jev isn't a chat model. You give it a **state**, such as an email, a support ticket or a review, along with a set of **typed questions**. It sends back structured answers: probabilities, picks from a list of options, or positions on a scale.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your key
```

`.env`:

```
OPENROUTER_API_KEY=sk-or-v1-...
JEV_MODEL=typesafe/jev-1.13        # or ~typesafe/jev-latest to track the newest release
```

## Question types

`jev.py` has helpers that build each question type:

| Helper | Type | Answer |
| --- | --- | --- |
| `noul(instructions, criteria=None)` | yes/no | a probability in `[0, 1]` |
| `choice(instructions, options)` | pick one | one of `options` (name → optional description), with a probability for each |
| `score(instructions, scale)` | ordered scale | a position on `scale`, listed from low to high |

## Library usage

```python
from jev import Jev, noul, choice, score

questions = {
    "needs_reply": noul("Does this email require a reply from me?"),
    "kind": choice("What kind of email is this?", {
        "meeting": "Scheduling or rescheduling a meeting",
        "request": "Someone asking me to do something",
        "fyi": None,
        "spam": None,
    }),
    "priority": score("How soon should I deal with this?",
                      ["ignore", "this week", "today", "right now"]),
}

with Jev() as jev:
    result = jev.decide({"text": "Can we move tomorrow's sync to 3pm?"}, questions)
    print(result)
```

`Jev()` reads `OPENROUTER_API_KEY` and `JEV_MODEL` from the environment. `.env` values take precedence over variables already set in the shell. You can also pass `api_key=` and `model=` directly.

## Interactive CLI

`chat.py` loads a question set from JSON. Each line you type is sent as a state, and the decisions are printed back.

```bash
python chat.py                                  # defaults to questions/email_triage.json
python chat.py questions/support_ticket.json
```

Commands:

- `:q` quits.
- `:load <file>` reloads questions.
- `:show` prints the current questions.
- `:raw` toggles the raw JSON output.

## Example question sets

The `questions/` folder has these examples:

- `email_triage.json`: whether an email needs a reply, what kind of email it is, and its priority
- `support_ticket.json`: whether a ticket is about billing, the customer's tone, and urgency
- `review_sentiment.json`: whether the reviewer recommends the product, the review's main topic, and the likely star rating

To make your own set, write a JSON object that maps each question name to `{"type", "instructions", "criteria"}`.
