"""
BrandPost Agent — CLI entry point.

Usage:
    cd bonus_agent
    python run.py

To upload a reference image, include the file path anywhere in your message:
    "Here's my reference: /path/to/image.png — replicate background only"
"""
import sys
import re
import base64
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from agents import Runner
from agent import create_agent

IMAGE_PATTERN = re.compile(r'[^\s\'"]+\.(?:png|jpg|jpeg|webp|gif)', re.IGNORECASE)


def build_message(user_input: str) -> dict:
    """Build a plain or multipart message depending on whether an image path is detected."""
    match = IMAGE_PATTERN.search(user_input)
    if match:
        image_path = Path(match.group(0))
        if image_path.exists():
            ext = image_path.suffix.lower().lstrip(".")
            mime = "jpeg" if ext == "jpg" else ext
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            # OpenAI Responses API format (used by openai-agents SDK)
            return {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_input},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/{mime};base64,{b64}",
                    },
                ],
            }
    return {"role": "user", "content": user_input}


def main():
    agent = create_agent()
    conversation_history = []

    print("=" * 60)
    print("  BrandPost Agent — Instagram Content Generator")
    print("=" * 60)
    print("Tell me about your brand and I'll create on-trend")
    print("Instagram content for you.")
    print()
    print("Tip: include a local image path in your message to")
    print("upload a reference (e.g. 'reference: ./my_poster.png')")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        message = build_message(user_input)
        conversation_history.append(message)

        print("\nAgent: (thinking...)\n")
        try:
            result = Runner.run_sync(agent, input=conversation_history)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        agent_reply = result.final_output

        print(f"Agent: {agent_reply}\n")
        conversation_history = result.to_input_list()


if __name__ == "__main__":
    main()
