# BrandPost Agent

An AI-powered Instagram content generation agent. Give it a brand brief — it searches for trending topics, writes captions, and produces a poster with text overlay, all in one shot.

---

## What It Does

1. **Searches for current trending topics** relevant to your product or event (via Serper.dev)
2. **Generates 3 Instagram caption variants** per trend, with hashtags and a call-to-action
3. **Generates a background image** (via Pollinations.ai — free, no key required)
4. **Composites a person photo** onto the poster (optional)
5. **Overlays your text** with layout and font styling

All outputs are saved to `output/` as PNG files.

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/brandpost-agent.git
cd brandpost-agent
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

- **OpenAI API key**: required for GPT-4o (captions + agent reasoning). Get one at [platform.openai.com](https://platform.openai.com).
- **Serper API key**: required for trend search. Free tier (2,500 queries/month) at [serper.dev](https://serper.dev).
- **Image generation**: uses [Pollinations.ai](https://pollinations.ai) — no API key needed.

### 3. Run

```bash
python run.py
```

---

## Usage

Type your brand brief in one message. The more detail you provide upfront, the better — the agent will generate content immediately without asking follow-up questions.

### Minimal prompt
```
Brand: Cha Cha
Product: new matcha latte "Morning Ritual"
Style: soft, minimal, warm Japanese aesthetic, earthy green tones
Text — Title: "Morning Ritual" | Subtitle: "Now Available" | Body: "Cha Cha × Spring 2025"
Layout: bottom-center
Generate 2 Instagram content packages.
```

### Full prompt (recommended)
```
Brand: [Brand Name]
Product/Event: [Description]
Target audience: [Who you're targeting]
Style: [Visual mood, color palette]
Background: [What should be in the image — e.g. "a matcha latte on a wooden table, soft morning light"]
Text — Title: "..." | Subtitle: "..." | Body: "..."
Text color: white / black / gold / cyan
Layout: bottom-center / split / editorial / centered / top-center / bottom-left / top-left
Font style: modern / luxury / editorial / classic / bold / minimal
Generate [N] trend-informed Instagram content packages.
```

### Reference image upload
Include a local file path anywhere in your message:
```
Here's my reference poster: /path/to/image.png — replicate background only
```
The agent will analyze the image and use it to guide generation.

---

## Tools

| Tool | Description |
|------|-------------|
| `search_trending_topics` | Searches Google for current trends relevant to the product/event category |
| `generate_captions` | Generates 3 brand-consistent Instagram captions with hashtags per trend |
| `generate_image` | Generates a background image via Pollinations.ai (no text, no faces) |
| `add_text_overlay` | Overlays title, subtitle, and body text with layout + font styling |
| `composite_person_on_poster` | Composites a person photo onto the background with edge feathering |

---

## Layout Options

| Layout | Best For |
|--------|----------|
| `bottom-center` | Product shots, lifestyle content |
| `split` | Speaker events (title top, details bottom) |
| `editorial` | Bold brand statements, oversized title |
| `centered` | Announcements, short copy |
| `top-center` / `top-left` | When the main visual is at the bottom |
| `bottom-left` | Casual, editorial feel |

## Font Style Options

| Style | Font | Best For |
|-------|------|----------|
| `modern` | Futura | Tech, startup, AI brands |
| `luxury` | Bodoni 72 | Fashion, beauty, premium |
| `editorial` | Didot + GillSans | Culture, arts, magazine |
| `classic` | Baskerville | Academic, institutional |
| `bold` | Rockwell | Sports, streetwear |
| `minimal` | GillSans | Food, lifestyle, approachable |

> Font availability depends on your OS. These fonts ship with macOS. On Linux/Windows, the agent falls back to a system default.

---

## Output

Generated files are saved to `output/`:

- `{brand}_{timestamp}.png` — background image
- `{brand}_{timestamp}_person.png` — background + person composite (if used)
- `{brand}_{timestamp}_text.png` — final poster with text overlay

---

## Notes

- Image generation uses Pollinations.ai (free, no key required). For higher quality, replace the `generate_image` tool with an OpenAI Images API call.
- The agent does not post to Instagram automatically. All outputs are local files for manual review and upload.
- Python 3.10+ recommended.
