"""
Standalone test for ZhipuAIService.analyze_clothing_image().
Run from project root: python test_vision.py
"""
import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import ZhipuAIService


async def main() -> None:
    uploads = Path("uploads")
    if not uploads.exists():
        print("ERROR: uploads/ folder not found. Run from the project root.")
        sys.exit(1)

    # Collect candidate images, prefer the largest (most likely a real photo)
    candidates = sorted(
        list(uploads.glob("*.jpg")) +
        list(uploads.glob("*.jpeg")) +
        list(uploads.glob("*.png")) +
        list(uploads.glob("*.webp")),
        key=lambda p: p.stat().st_size,
        reverse=True,
    )

    if not candidates:
        print("ERROR: No images found in uploads/.")
        sys.exit(1)

    img_path = candidates[0]
    image_bytes = img_path.read_bytes()

    print(f"Image : {img_path.name}")
    print(f"Size  : {len(image_bytes):,} bytes")
    print(f"Model : glm-4v-plus")
    print("-" * 50)

    service = ZhipuAIService()
    result = await service.analyze_clothing_image(image_bytes)

    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
