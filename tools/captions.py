import json
from openai import OpenAI
from agents import function_tool


@function_tool
def generate_captions(
    brand_name: str,
    product_description: str,
    trend: str,
    style: str,
    target_audience: str,
) -> str:
    """
    Generate 3 Instagram caption variants for a product, incorporating a current trend.
    Each caption includes relevant hashtags and a call-to-action.
    Returns a JSON string with a list of 3 captions.
    """
    client = OpenAI()

    prompt = f"""You are an expert Instagram content creator.

Brand: {brand_name}
Product: {product_description}
Current trend to incorporate: {trend}
Visual/tone style: {style}
Target audience: {target_audience}

Write 3 distinct Instagram captions for this product. Each caption must:
- Be 2-4 sentences long
- Naturally weave in the current trend
- Match the brand's style and tone
- End with 5-8 relevant hashtags
- Include a clear call-to-action

Return ONLY a JSON object in this exact format:
{{
  "captions": [
    {{"caption": "...", "hashtags": "#tag1 #tag2 ..."}},
    {{"caption": "...", "hashtags": "#tag1 #tag2 ..."}},
    {{"caption": "...", "hashtags": "#tag1 #tag2 ..."}}
  ]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    return response.choices[0].message.content
