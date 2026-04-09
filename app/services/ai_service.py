from __future__ import annotations

import json
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.config import settings
from app.models.clothing import Clothing

logger = logging.getLogger(__name__)

VALID_OCCASIONS = {"Casual", "Formal", "Sport", "Date", "Work"}
VALID_STYLES = {"Minimalist", "Vintage", "Streetwear", "Professional"}


@dataclass
class AIOutfitRecommendation:
    # Note: IDs are str UUIDs to match Clothing.id — spec said list[int] but
    # our primary keys are String(36) UUID4 values.
    selected_item_ids: list[str]
    ai_explanation: str
    ai_score: float  # 1.0–10.0
    improvement_suggestions: str = ""


class BaseAIService(ABC):
    @abstractmethod
    async def generate_outfit(
        self,
        clothing_items: list[Clothing],
        occasion: str,
        weather_context: str | None = None,
        style_preference: str | None = None,
    ) -> list[AIOutfitRecommendation]:
        ...

    @staticmethod
    def _validate_inputs(occasion: str, style_preference: str | None) -> None:
        if occasion not in VALID_OCCASIONS:
            raise ValueError(
                f"Invalid occasion '{occasion}'. Must be one of: {sorted(VALID_OCCASIONS)}"
            )
        if style_preference is not None and style_preference not in VALID_STYLES:
            raise ValueError(
                f"Invalid style '{style_preference}'. Must be one of: {sorted(VALID_STYLES)}"
            )


class MockAIService(BaseAIService):
    async def generate_outfit(
        self,
        clothing_items: list[Clothing],
        occasion: str,
        weather_context: str | None = None,
        style_preference: str | None = None,
    ) -> list[AIOutfitRecommendation]:
        logger.warning("MockAIService is active — not suitable for production")
        self._validate_inputs(occasion, style_preference)

        if not clothing_items:
            raise ValueError("No clothing items provided for outfit generation")

        style_note = f" with a {style_preference} aesthetic" if style_preference else ""
        weather_note = f" suited for {weather_context}" if weather_context else ""

        recommendations: list[AIOutfitRecommendation] = []
        used_sets: list[frozenset] = []
        attempts = 0

        while len(recommendations) < 3 and attempts < 30:
            attempts += 1
            count = min(random.randint(2, 4), len(clothing_items))
            selected = random.sample(clothing_items, count)
            key = frozenset(item.id for item in selected)
            if key in used_sets:
                continue
            used_sets.append(key)
            categories = [f"{item.sub_category} ({item.color_code})" for item in selected]
            explanation = (
                f"For a {occasion.lower()} occasion{style_note}{weather_note}, "
                f"this outfit pairs {', '.join(categories[:-1])} with {categories[-1]}. "
                f"The combination balances color and material for a cohesive look."
            )
            recommendations.append(AIOutfitRecommendation(
                selected_item_ids=[item.id for item in selected],
                ai_explanation=explanation,
                ai_score=round(random.uniform(5.0, 9.0), 1),
            ))

        recommendations.sort(key=lambda r: r.ai_score, reverse=True)
        return recommendations


# --------------------------------------------------------------------------- #
# System prompt used by AnthropicAIService.                                   #
# --------------------------------------------------------------------------- #
_SYSTEM_PROMPT = """You are an expert fashion stylist AI for SmartWardrobe.
Select clothing items from the user's wardrobe and compose a complete outfit.

RULES:
- Respond with valid JSON ONLY — no prose, no markdown, no code fences.
- Select between 2 and 4 items from the provided list.
- Use ONLY item IDs present in the input list.
- Selected items must form a coherent, complete outfit.

SCORE RUBRIC (ai_score, float 1.0–10.0):
- 10  : Perfect match for all constraints, excellent color/style coordination
- 7-9 : Strong match, minor compromises
- 4-6 : Acceptable outfit, notable gaps in constraints or coordination
- 1-3 : Weak match — limited wardrobe options forced poor choices

VALID OCCASIONS : Casual, Formal, Sport, Date, Work
VALID STYLES    : Minimalist, Vintage, Streetwear, Professional

OUTPUT FORMAT (strict JSON, no other text):
{
  "selected_item_ids": ["<uuid>", ...],
  "ai_explanation": "<human-readable reasoning, 2-4 sentences>",
  "ai_score": <float between 1.0 and 10.0>
}"""


class AnthropicAIService(BaseAIService):
    async def generate_outfit(
        self,
        clothing_items: list[Clothing],
        occasion: str,
        weather_context: str | None = None,
        style_preference: str | None = None,
    ) -> AIOutfitRecommendation:
        self._validate_inputs(occasion, style_preference)

        if not clothing_items:
            raise ValueError("No clothing items provided for outfit generation")

        items_payload = [
            {
                "id": item.id,
                "category": item.category,
                "sub_category": item.sub_category,
                "color_code": item.color_code,
                "material": item.material,
                "season": item.season,
            }
            for item in clothing_items
        ]

        user_message = (
            f"Constraints:\n"
            f"- Occasion: {occasion}\n"
            f"- Weather context: {weather_context or 'not specified'}\n"
            f"- Style preference: {style_preference or 'not specified'}\n\n"
            f"Available wardrobe items:\n{items_payload}\n\n"
            f"Respond with JSON only."
        )

        # ------------------------------------------------------------------ #
        # TODO: Implement the real API call here when AI_PROVIDER=anthropic.  #
        #                                                                      #
        # import json                                                          #
        # import anthropic                                                     #
        #                                                                      #
        # client = anthropic.AsyncAnthropic(                                  #
        #     api_key=settings.ANTHROPIC_API_KEY                              #
        # )                                                                    #
        # response = await client.messages.create(                            #
        #     model="claude-opus-4-6",                                        #
        #     max_tokens=512,                                                  #
        #     system=_SYSTEM_PROMPT,                                          #
        #     messages=[{"role": "user", "content": user_message}],           #
        # )                                                                    #
        # raw = json.loads(response.content[0].text)                          #
        # return AIOutfitRecommendation(                                       #
        #     selected_item_ids=raw["selected_item_ids"],                     #
        #     ai_explanation=raw["ai_explanation"],                            #
        #     ai_score=float(raw["ai_score"]),                                #
        # )                                                                    #
        # ------------------------------------------------------------------ #

        if not settings.ANTHROPIC_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env.",
            )

        raise NotImplementedError(
            "AnthropicAIService.generate_outfit() is not yet implemented. "
            "Set AI_PROVIDER=mock in .env to use MockAIService."
        )


# --------------------------------------------------------------------------- #
# Prompt shared by GeminiAIService (same contract as _SYSTEM_PROMPT above).   #
# --------------------------------------------------------------------------- #
_GEMINI_SYSTEM_PROMPT = """You are an expert fashion stylist AI for SmartWardrobe.
Select clothing items from the user's wardrobe and compose a complete outfit.

RULES:
- Respond with valid JSON ONLY — no prose, no markdown, no code fences.
- Select between 2 and 4 items from the provided list.
- Use ONLY item IDs present in the input list.
- Selected items must form a coherent, complete outfit.

SCORE RUBRIC (ai_score, float 1.0–10.0):
- 10  : Perfect match for all constraints, excellent color/style coordination
- 7-9 : Strong match, minor compromises
- 4-6 : Acceptable outfit, notable gaps in constraints or coordination
- 1-3 : Weak match — limited wardrobe options forced poor choices

VALID OCCASIONS : Casual, Formal, Sport, Date, Work
VALID STYLES    : Minimalist, Vintage, Streetwear, Professional

OUTPUT FORMAT (strict JSON, no other text):
{
  "selected_item_ids": ["<uuid>", ...],
  "ai_explanation": "<human-readable reasoning, 2-4 sentences>",
  "ai_score": <float between 1.0 and 10.0>
}"""


class GeminiAIService(BaseAIService):
    async def generate_outfit(
        self,
        clothing_items: list[Clothing],
        occasion: str,
        weather_context: str | None = None,
        style_preference: str | None = None,
    ) -> list[AIOutfitRecommendation]:
        self._validate_inputs(occasion, style_preference)

        if not clothing_items:
            raise ValueError("No clothing items provided for outfit generation")

        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key not configured. Set GEMINI_API_KEY in .env.",
            )

        items_payload = [
            {
                "id": item.id,
                "category": item.category,
                "sub_category": item.sub_category,
                "color_code": item.color_code,
                "material": item.material,
                "season": item.season,
            }
            for item in clothing_items
        ]

        user_message = (
            f"Constraints:\n"
            f"- Occasion: {occasion}\n"
            f"- Weather context: {weather_context or 'not specified'}\n"
            f"- Style preference: {style_preference or 'not specified'}\n\n"
            f"Available wardrobe items:\n{json.dumps(items_payload, indent=2)}\n\n"
            f"Respond with JSON only."
        )

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=_GEMINI_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            raw = json.loads(response.text)
        except json.JSONDecodeError as exc:
            logger.error("Gemini returned non-JSON: %s", response.text[:200])
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini returned invalid JSON: {exc}",
            )
        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini API call failed: {exc}",
            )

        return [AIOutfitRecommendation(
            selected_item_ids=raw["selected_item_ids"],
            ai_explanation=raw["ai_explanation"],
            ai_score=float(raw["ai_score"]),
        )]


# --------------------------------------------------------------------------- #
# System prompt used by ZhipuAIService.                                        #
# --------------------------------------------------------------------------- #
_ZHIPU_SYSTEM_PROMPT = """重要：你必须用简体中文回复所有文字内容。
explanation字段和improvement_suggestions字段必须用中文写。
严禁使用英文。

You are an expert fashion stylist AI for SmartWardrobe.
Generate 3 different outfit combinations from the user's wardrobe items.

RULES:
- Respond with valid JSON ONLY — no prose, no markdown, no code fences.
- Each outfit must select 2–4 items from the provided list.
- Use ONLY item IDs present in the input list.
- Each outfit must use a DIFFERENT combination of items — no two outfits may have identical selected_item_ids sets.
- Each outfit must form a coherent, complete look.

EXPLANATION REQUIREMENTS (per outfit):
Write exactly 3–4 sentences covering all four points in order:
1. COLOR & STYLE HARMONY — why the specific colors and styles work together.
2. OCCASION FIT — why this combination suits the given occasion and style preference.
3. STYLING TIP — one concrete, actionable tip (e.g. "tuck the shirt in for a cleaner silhouette").
4. ACCESSORY SUGGESTION — one specific accessory that would complete the look.

SCORE RUBRIC (score, float 1.0–10.0) — score strictly:
- 8.0–10.0 (A): Cohesive, occasion-appropriate, and genuinely stylish.
- 5.0–7.9  (B): Works but has at least one minor style or color mismatch.
- 1.0–4.9  (C): Notable style conflicts, poor color pairing, or weak occasion fit.

IMPROVEMENT SUGGESTIONS RULES (improvement_suggestions field):
- Score >= 8.0: set improvement_suggestions to "" (empty string).
- Score 5.0–7.9: provide 2–3 specific, actionable suggestions referencing the actual items chosen.
- Score < 5.0: provide 3–4 stronger suggestions explaining what is clashing or missing and what to add or replace.
- All suggestions must reference the specific items selected by name.

LANGUAGE: Please write the explanation and improvement_suggestions fields in Chinese (Simplified). All other fields (selected_item_ids, score) remain unchanged.

ORDERING: Sort the 3 outfits by score descending (highest score first).

VALID OCCASIONS : Casual, Formal, Sport, Date, Work
VALID STYLES    : Minimalist, Vintage, Streetwear, Professional

OUTPUT FORMAT (strict JSON, no other text):
{
  "outfits": [
    {
      "selected_item_ids": ["<uuid>", ...],
      "explanation": "<3-4 sentences: color/style harmony, occasion fit, styling tip, accessory suggestion>",
      "score": <float between 1.0 and 10.0>,
      "improvement_suggestions": "<empty string if score >= 8.0, otherwise 2-4 specific suggestions>"
    },
    { "<second outfit, different items>" },
    { "<third outfit, different items>" }
  ]
}"""


class ZhipuAIService(BaseAIService):
    async def generate_outfit(
        self,
        clothing_items: list[Clothing],
        occasion: str,
        weather_context: str | None = None,
        style_preference: str | None = None,
    ) -> AIOutfitRecommendation:
        import asyncio
        from zhipuai import ZhipuAI

        self._validate_inputs(occasion, style_preference)

        if not clothing_items:
            raise ValueError("No clothing items provided for outfit generation")

        if not settings.ZHIPU_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ZhipuAI API key not configured. Set ZHIPU_API_KEY in .env.",
            )

        items_payload = [
            {
                "id": item.id,
                "category": item.category,
                "sub_category": item.sub_category,
                "color_code": item.color_code,
                "material": item.material,
                "season": item.season,
            }
            for item in clothing_items
        ]

        user_message = (
            f"Constraints:\n"
            f"- Occasion: {occasion}\n"
            f"- Weather context: {weather_context or 'not specified'}\n"
            f"- Style preference: {style_preference or 'not specified'}\n\n"
            f"Available wardrobe items:\n{json.dumps(items_payload, indent=2)}\n\n"
            f"Respond with JSON only."
        )

        user_message += "\n请用中文回复explanation和improvement_suggestions字段。"

        # zhipuai SDK is synchronous — run in a thread to avoid blocking the event loop
        def _call_api() -> str:
            client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
            response = client.chat.completions.create(
                model="glm-4v-plus",
                messages=[
                    {"role": "system", "content": _ZHIPU_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content

        try:
            raw_text = await asyncio.to_thread(_call_api)
        except Exception as exc:
            logger.error("ZhipuAI API call failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZhipuAI API call failed: {exc}",
            )

        # Strip markdown fences if the model wraps its JSON output
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        try:
            raw = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("ZhipuAI returned non-JSON: %s", raw_text[:200])
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZhipuAI returned invalid JSON: {exc}",
            )

        outfits_data = raw.get("outfits", [])
        if not outfits_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ZhipuAI returned no outfits in response",
            )
        return [
            AIOutfitRecommendation(
                selected_item_ids=o["selected_item_ids"],
                ai_explanation=o["explanation"],
                ai_score=float(o["score"]),
                improvement_suggestions=o.get("improvement_suggestions", ""),
            )
            for o in outfits_data
        ]

    async def analyze_clothing_image(self, image_bytes: bytes) -> dict:
        """Send an image to GLM-4V-Plus and return structured clothing tags.

        Returns a dict with keys: category, sub_category, color_code, material, season.
        Returns {"error": "..."} if the image is not a recognisable clothing item.
        Raises HTTPException(503) on API or JSON-parsing failures.
        """
        import asyncio
        import base64
        from zhipuai import ZhipuAI

        if not settings.ZHIPU_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ZhipuAI API key not configured. Set ZHIPU_API_KEY in .env.",
            )

        # Detect MIME type from magic bytes so the data-URI is correct
        if image_bytes[:2] == b"\xff\xd8":
            mime_type = "image/jpeg"
        elif image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            mime_type = "image/png"
        elif image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"  # safe fallback

        data_uri = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode()}"

        def _call_api() -> str:
            client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
            response = client.chat.completions.create(
                model="glm-4v-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_uri},
                            },
                            {
                                "type": "text",
                                "text": _ZHIPU_VISION_PROMPT,
                            },
                        ],
                    }
                ],
            )
            return response.choices[0].message.content

        try:
            raw_text = await asyncio.to_thread(_call_api)
        except Exception as exc:
            logger.error("ZhipuAI vision call failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZhipuAI vision call failed: {exc}",
            )

        # Strip markdown fences if the model wraps its output
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("ZhipuAI vision returned non-JSON: %s", raw_text[:300])
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZhipuAI vision returned invalid JSON: {exc}",
            )


# --------------------------------------------------------------------------- #
# Vision prompt referenced by ZhipuAIService.analyze_clothing_image.          #
# --------------------------------------------------------------------------- #
_ZHIPU_VISION_PROMPT = """Analyze the clothing item in this image and return a JSON object
with exactly these fields:

{
  "category": "Top" | "Bottom" | "Shoes" | "Outerwear" | "Accessory",
  "sub_category": "<descriptive name, e.g. White Oxford Shirt>",
  "color_code": "<dominant color as 6-digit hex, e.g. #FFFFFF>",
  "material": "<best guess, e.g. Cotton>",
  "season": ["spring" | "summer" | "autumn" | "winter"]
}

Rules:
- Respond with valid JSON ONLY — no markdown fences, no prose, no extra keys.
- season must be an array containing one or more of the four values.
- color_code must be exactly # followed by 6 hex digits.
- If the image is unclear or does not contain a clothing item, return exactly:
  {"error": "Could not identify clothing item"}"""


def get_ai_service() -> BaseAIService:
    provider = settings.AI_PROVIDER.lower()
    if provider == "mock":
        return MockAIService()
    if provider == "anthropic":
        return AnthropicAIService()
    if provider == "gemini":
        return GeminiAIService()
    if provider == "zhipu":
        return ZhipuAIService()
    raise ValueError(
        f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}'. "
        f"Must be 'mock', 'anthropic', 'gemini', or 'zhipu'."
    )
