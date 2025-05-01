from openai import OpenAI

def generate_story(prompt: str, api_key: str) -> tuple[str, dict]:
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
    )

    story = response.choices[0].message.content
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "estimated_cost_usd": estimate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
    }

    return story, usage


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Estimate the cost of a single request based on GPT-4o pricing.
    (Input tokens = $0.005 per 1000, Output tokens = $0.015 per 1000)
    """
    input_cost = (prompt_tokens / 1000) * 0.005
    output_cost = (completion_tokens / 1000) * 0.015
    return round(input_cost + output_cost, 6)
