"""One tiny real call to check that your key, URL and model work.
Run from the project folder:  python smoke_test.py
Costs only a few Aikredits (short question, 60-token answer)."""

from core import llm_client

result = llm_client.ask(
    [{"role": "user", "content": "Reply with exactly: LakbayLigtas connection OK"}],
    max_tokens=60,
)
if result.ok:
    print("SUCCESS:", result.text)
    print(f"Tokens in/out: {result.prompt_tokens}/{result.completion_tokens}  (about {result.estimated_ak} AK)")
else:
    print("FAILED:", result.error)
