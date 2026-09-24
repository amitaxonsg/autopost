import base64
import json
from openai import OpenAI

def test_openai(api_key: str, model: str) -> tuple[bool, str]:
    if not api_key:
        return False, "API key is empty."
    try:
        client = OpenAI(api_key=api_key)
        r = client.responses.create(model=model, input="Reply with exactly: OK", max_output_tokens=8)
        text = (r.output_text or "").strip()
        return ("OK" in text.upper()), (text or "Connected")
    except Exception as exc:
        return False, str(exc)

def generate_article(api_key: str, model: str, topic, memory_text: str) -> dict:
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured.")
    client = OpenAI(api_key=api_key)
    prompt = f"""You are preparing a WordPress blog draft for a real business.

CLIENT MEMORY / BRAND RULES:
{memory_text}

TOPIC:
{topic.title}

KEYWORDS:
{topic.keywords}

CATEGORY:
{topic.category}

EDITOR NOTES:
{topic.notes}

Return ONLY valid JSON with these keys:
title, excerpt, meta_description, category, tags, image_prompt, image_alt, content_html

Rules:
- Write useful, natural, non-hype content.
- Never invent business facts, awards, prices, opening hours, menu items, promotions, testimonials, or availability.
- Follow the client memory strictly.
- Use clean semantic HTML suitable for WordPress.
- Use short paragraphs and clear H2/H3 headings.
- tags must be an array of short strings.
- Do not wrap JSON in markdown fences.
"""
    r = client.responses.create(model=model, input=prompt)
    raw = (r.output_text or "").strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "", 1).replace("```", "").strip()
    data = json.loads(raw)
    required = ["title", "excerpt", "meta_description", "content_html", "image_prompt", "image_alt"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise RuntimeError("AI response missing required fields: " + ", ".join(missing))
    if not isinstance(data.get("tags", []), list):
        data["tags"] = []
    return data

def generate_image_bytes(api_key: str, image_model: str, prompt: str) -> tuple[bytes, str]:
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured.")
    client = OpenAI(api_key=api_key)
    result = client.images.generate(model=image_model, prompt=prompt, size="1536x1024", quality="low")
    item = result.data[0]
    if getattr(item, "b64_json", None):
        return base64.b64decode(item.b64_json), "image/png"
    if getattr(item, "url", None):
        import requests
        r = requests.get(item.url, timeout=60)
        r.raise_for_status()
        return r.content, r.headers.get("content-type", "image/png")
    raise RuntimeError("Image API returned no image data.")
