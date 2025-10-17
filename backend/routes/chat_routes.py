from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import re

from services.config import Settings
from services.grok_service import GrokService
from services.doc_retriever import DocRetriever
from services.support_tools import build_user_context
from services.support_tools import text_to_vec, cosine_similarity
from services.auth_service import get_optional_current_user
from schemas.user_schema import UserResponse
from models.user import users_collection
from bson import ObjectId

# Create router
router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    message: str
    page: Optional[str] = None
    formSummary: Optional[Dict[str, Any]] = None
    lastResults: Optional[Dict[str, Any]] = None
    includeUserContext: Optional[bool] = False


class ChatResponse(BaseModel):
    reply: str


# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "You are a friendly and helpful customer service assistant for our travel cost estimation company. "
    "Give clear, short answers. Be specific to how THIS site works: multi-agent (LangGraph) orchestration, "
    "country-aware pricing, domestic vs international routing, 2 travelers per room for accommodation, and vibe personalization. "
    "If a question needs user/account data or a fresh estimate, explain which page/step to use rather than inventing data."
)


# Initialize Grok and retriever once
settings = Settings()
grok = GrokService(settings)
_retriever: Optional[DocRetriever] = None


def _get_retriever() -> DocRetriever:
    global _retriever
    if _retriever is not None:
        return _retriever
    project_root = "."  # backend runs from project root by default in dev
    docs: List[str] = [
        "COMPLETE_SYSTEM_OVERVIEW.md",
        "INTELLIGENT_PRICING_SYSTEM.md",
        "LLM_PRICING_AGENT_IMPLEMENTATION.md",
        "FINAL_SYSTEM_STATUS.md",
        "AI_CUSTOMER_SUPPORT_CHATBOT.md",
        "UI_CHANGES_SUMMARY.md",
        "UI_DOMESTIC_TRAVEL_CHANGES.md",
        "TRANSPORTATION_PRICING_EXPLAINED.md",
        "PRICE_CALENDAR_UI_INTEGRATION.md",
        "PRICE_CALENDAR_INVESTIGATION_RESULTS.md",
        "TRANSPORTATION_COST_FIX.md",
        "FOOD_COST_ESTIMATOR_IMPLEMENTATION.md",
        "HOTEL_COST_CALCULATION_EXPLAINED.md",
        "FINAL_TRANSPORTATION_FIXES.md",
        "DISTANCE_AND_FOOD_COST_FIXES.md",
        "COST_CALCULATION_FIX.md",
        "COST_ESTIMATION_FIX.md",
        # Add code-grounded docs: key routes and services (read as text)
        "backend/routes/auth_routes.py",
        "backend/routes/subscription_routes.py",
        "backend/routes/chat_routes.py",
        "backend/main.py",
        "backend/services/stripe_service.py",
        "backend/services/intelligent_pricing_service.py",
        "backend/services/price_calendar.py",
        "backend/services/hotel_search.py",
        "backend/services/flight_search.py",
    ]
    _retriever = DocRetriever(project_root=project_root, documents=docs)
    return _retriever


def _format_context_block(snippets: List[tuple]) -> str:
    if not snippets:
        return ""
    lines: List[str] = ["[Site Docs]"]
    for src, chunk in snippets:
        lines.append(f"Source: {src}\n{chunk.strip()}\n")
    return "\n".join(lines)


def _format_remaining_generations(user: Optional[UserResponse]) -> Optional[str]:

    if not user:
        return None
    try:
        # Fetch fresh data from DB to avoid stale values on the model
        db_user = users_collection.find_one({"email": user.email})
        if not db_user:
            return None

        user_type = db_user.get("type", user.type)
        status = db_user.get("subscriptionStatus", user.subscriptionStatus)
        end_date = db_user.get("subscriptionEndDate", user.subscriptionEndDate)

        if user_type == "premium" and status == "active":
            # Premium users are effectively unlimited until subscription end
            if end_date:
                return f"You're on premium. Generations are unlimited until {end_date.date()}."  # type: ignore[union-attr]
            return "You're on premium. Generations are unlimited while your subscription is active."
        # Basic: show remaining integer
        remaining = int(db_user.get("generationsRemaining", 0))
        return f"You have {remaining} generation(s) remaining on your basic plan."
    except Exception:
        return None


def _is_remaining_plans_question(text: str) -> bool:
    q = text.lower()
    keywords = [
        "generations left", "generation left", "remaining generations", "plans left",
        "remaining plans", "how many generations", "quota left", "usage left",
        "how many plans i have", "how many plans do i have", "how many plan i have",
        "how many plan do i have", "plans do i have", "how many left", "left plans",
    ]
    if any(k in q for k in keywords):
        return True

    # Semantic token matcher: handles variants like
    # "how many plans do I have", "how many generations are left" etc.
    def normalize(s: str) -> List[str]:
        s = s.lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        tokens = [t for t in s.split() if t]
        # basic stemming/synonyms
        synonyms = {
            "plans": "plan", "plan": "plan",
            "generations": "generation", "generation": "generation", "gen": "generation",
            "left": "left", "remaining": "left",
            "have": "have", "got": "have",
            "how": "how", "many": "many",
        }
        return [synonyms.get(t, t) for t in tokens]

    toks = normalize(text)
    token_set = set(toks)

    # Core concept words must appear
    has_quantity = "how" in token_set and "many" in token_set
    has_resource = ("plan" in token_set) or ("generation" in token_set)
    has_state = ("have" in token_set) or ("left" in token_set)

    return has_quantity and has_resource and has_state


# --- Deterministic intent templates ---
def _intent_reply(user_text: str) -> Optional[str]:
    q = user_text.strip().lower()

    cultural_keys = ["cultural vibe", "what does the cultural", "cultural change", "cultural effect"]
    if any(k in q for k in cultural_keys):
        return (
            "Cultural adjusts the plan toward museums, heritage sites, guided tours and local eateries. "
            "Budget shifts from nightlife/shopping to admissions and tours. Example: for a 4‑day city break, expect 2–3 museum entries (€45–€70 total) and a slower daily pace. "
            "Select ‘Cultural’ on the Travel page to see the exact activity mix and price changes for your route."
        )

    romantic_keys = ["romantic vibe", "romantic affect", "romantic activities", "romantic food"]
    if any(k in q for k in romantic_keys):
        return (
            "Romantic prioritizes sunset viewpoints, spas, scenic walks, and intimate restaurants. It increases the chance of a private tour/cruise and biases dining to mid–high tier spots. "
            "Typical impact: +€15–€40/day on dining and +€30–€80 for one private experience. Choose ‘Romantic’ to preview a sample day and updated totals."
        )

    security_keys = ["security", "privacy", "protect my security", "data secure", "is my data safe"]
    if any(k in q for k in security_keys):
        return (
            "We use HTTPS, JWT-based sessions, bcrypt password hashing, and Stripe for payments (we don’t store cards), plus rate limiting. "
            "You can review/delete your data under Account → Privacy. See our Privacy Policy for full details."
        )

    upgrade_keys = ["how to upgrade", "upgrade plan", "go premium", "buy subscription", "subscribe"]
    if any(k in q for k in upgrade_keys):
        return (
            "To upgrade to Premium: 1) Log in. 2) Go to Account → Upgrade (or Pricing). 3) Click ‘Upgrade to Premium’. This calls POST /subscription/create-checkout-session and redirects you to Stripe Checkout. "
            "After payment, we activate Premium automatically via webhooks; your plan shows as ‘active’ and generations become unlimited."
        )

    return None


def _classify_intent_by_similarity(user_text: str) -> Optional[str]:
    """Lightweight embeddings via bag-of-words cosine.
    Returns one of: remaining_plans, vibe_cultural, vibe_romantic, security, or None.
    """
    templates = {
        "remaining_plans": [
            "how many generations do i have left",
            "how many plans i have",
            "remaining plans",
            "what is my quota left",
        ],
        "vibe_cultural": [
            "what does the cultural vibe change",
            "cultural effect on plan",
            "how cultural affects trip",
        ],
        "vibe_romantic": [
            "how does romantic affect activities and food",
            "romantic vibe impact",
            "romantic effect",
        ],
        "security": [
            "how does this system protect my security",
            "is my data safe",
            "privacy and security details",
        ],
        "upgrade": [
            "how to upgrade",
            "upgrade plan",
            "go premium",
            "buy subscription",
            "subscribe",
        ],
    }

    user_vec = text_to_vec(user_text)
    best_label = None
    best_score = 0.0
    for label, phrases in templates.items():
        # Average similarity over phrases
        scores = []
        for p in phrases:
            scores.append(cosine_similarity(user_vec, text_to_vec(p)))
        avg = sum(scores) / len(scores) if scores else 0.0
        if avg > best_score:
            best_score = avg
            best_label = label

    # Threshold to avoid accidental matches
    return best_label if best_score >= 0.35 else None


def _is_last_estimate_summary_question(text: str) -> bool:
    q = text.lower().strip()
    if not q:
        return False
    keys = [
        "summarize my last estimate",
        "summary of last estimate",
        "summarize last plan",
        "last estimate summary",
        "recap my last estimate",
        "recap last plan",
    ]
    return any(k in q for k in keys)


def _summarize_last_results(last: Dict[str, Any]) -> str:
    try:
        if not last:
            return "I couldn't find a previous estimate in this session. Please run a new estimate on the Travel page."
        origin = last.get("vibe_analysis", {}).get("origin") or last.get("origin")
        destination = last.get("vibe_analysis", {}).get("destination") or last.get("destination")
        total_cost = last.get("total_cost")
        currency = last.get("currency", "USD")
        cb = last.get("cost_breakdown", {})
        flights = cb.get("flights")
        accommodation = cb.get("accommodation")
        transportation = cb.get("transportation")
        activities = cb.get("activities")
        food = cb.get("food")
        miscellaneous = cb.get("miscellaneous")
        nights = None
        try:
            itin = last.get("itinerary") or []
            nights = len(itin)
        except Exception:
            nights = None

        lines = []
        if origin and destination:
            lines.append(f"Trip: {origin} → {destination}")
        if nights:
            lines.append(f"Duration: ~{nights} day(s)")
        if isinstance(total_cost, (int, float)):
            lines.append(f"Total estimated cost: {total_cost:,.2f} {currency}")
        parts = []
        def add(label, value):
            if isinstance(value, (int, float)):
                parts.append(f"- {label}: {value:,.2f} {currency}")
        add("Flights", flights)
        add("Accommodation", accommodation)
        add("Transportation", transportation)
        add("Activities", activities)
        add("Food", food)
        add("Misc.", miscellaneous)
        if parts:
            lines.append("Breakdown:\n" + "\n".join(parts))

        recs = last.get("recommendations") or []
        if recs:
            lines.append("Top tips:\n- " + "\n- ".join(recs[:3]))

        return "\n".join(lines) if lines else "I found your last estimate, but it looks incomplete. Try generating a fresh one from the Travel page."
    except Exception:
        return "I couldn't summarize the last estimate due to an unexpected error. Please generate a new estimate on the Travel page."


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    try:
        if not grok.initialized:
            await grok.initialize()

        # Short-circuit for remaining generations intent
        if _is_remaining_plans_question(request.message):
            remaining_text = _format_remaining_generations(current_user)
            if remaining_text:
                return ChatResponse(reply=remaining_text)
            else:
                return ChatResponse(reply="Please sign in to view your remaining generations. You can check it on the Account page as well.")

        # Deterministic content intents
        templated = _intent_reply(request.message)
        if templated:
            return ChatResponse(reply=templated)

        # Embedding-style similarity classifier to route to templates
        intent = _classify_intent_by_similarity(request.message)
        if intent == "remaining_plans":
            remaining_text = _format_remaining_generations(current_user)
            return ChatResponse(reply=remaining_text or "Please sign in to view your remaining generations. You can check it on the Account page as well.")
        elif intent in ("vibe_cultural", "vibe_romantic", "security", "upgrade"):
            templ = _intent_reply(request.message) or _intent_reply(intent.replace("_", " "))
            if templ:
                return ChatResponse(reply=templ)

        # Short-circuit for summarizing last estimate if client sent data
        if _is_last_estimate_summary_question(request.message) and request.lastResults:
            summary = _summarize_last_results(request.lastResults)  # type: ignore[arg-type]
            return ChatResponse(reply=summary)

        # Retrieve site knowledge
        retriever = _get_retriever()
        snippets = retriever.retrieve(request.message, k=4)
        context_block = _format_context_block(snippets)

        # Build optional page/form context
        page_block = f"[Page] {request.page}" if request.page else ""
        form_block = ""
        if request.formSummary:
            try:
                origin = request.formSummary.get("origin")
                destination = request.formSummary.get("destination")
                vibe = request.formSummary.get("vibe") or request.formSummary.get("selectedVibe")
                start_date = request.formSummary.get("startDate")
                return_date = request.formSummary.get("returnDate")
                form_lines = ["[Form]", f"origin: {origin}", f"destination: {destination}", f"startDate: {start_date}", f"returnDate: {return_date}", f"vibe: {getattr(vibe, 'name', vibe)}"]
                form_block = "\n".join([l for l in form_lines if l is not None])
            except Exception:
                pass

        # Optionally include user context (auth-based); failures are ignored
        user_block = ""
        try:
            user_ctx = await build_user_context(request.includeUserContext)  # type: ignore[arg-type]
            if user_ctx:
                user_block = f"[User]\n{user_ctx}"
        except Exception:
            pass

        composed = "\n\n".join([b for b in [context_block, page_block, form_block, user_block] if b])
        if composed:
            user_prompt = f"Context below may help. Use it only if relevant.\n\n{composed}\n\nUser: {request.message}"
        else:
            user_prompt = request.message

        reply = await grok.generate_response(prompt=user_prompt, system_message=SYSTEM_PROMPT, force_json=False)
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat service failed")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Simple streaming endpoint that sends newline-delimited JSON chunks.
    For now we buffer Grok output and stream it as one chunk to keep compatibility; can be upgraded to true token streaming later.
    """
    try:
        if not grok.initialized:
            await grok.initialize()

        # Short-circuit for remaining generations intent (streamed as one chunk)
        if _is_remaining_plans_question(request.message):
            import json
            remaining_text = _format_remaining_generations(current_user) or "Please sign in to view your remaining generations. You can check it on the Account page as well."

            async def event_generator_short():
                yield json.dumps({"reply": remaining_text}, ensure_ascii=False) + "\n"

            return StreamingResponse(event_generator_short(), media_type="application/json")

        # Deterministic content intents (streamed as one chunk)
        templated = _intent_reply(request.message)
        if templated:
            import json
            async def event_generator_template():
                yield json.dumps({"reply": templated}, ensure_ascii=False) + "\n"
            return StreamingResponse(event_generator_template(), media_type="application/json")

        # Embedding-style similarity classifier
        intent = _classify_intent_by_similarity(request.message)
        if intent == "remaining_plans":
            import json
            remaining_text = _format_remaining_generations(current_user) or "Please sign in to view your remaining generations. You can check it on the Account page as well."
            async def event_generator_embed():
                yield json.dumps({"reply": remaining_text}, ensure_ascii=False) + "\n"
            return StreamingResponse(event_generator_embed(), media_type="application/json")
        elif intent in ("vibe_cultural", "vibe_romantic", "security"):
            import json
            templ = _intent_reply(request.message) or _intent_reply(intent.replace("_", " "))
            async def event_generator_embed_t():
                yield json.dumps({"reply": templ or ""}, ensure_ascii=False) + "\n"
            return StreamingResponse(event_generator_embed_t(), media_type="application/json")
        elif intent == "upgrade":
            import json
            templ = _intent_reply("upgrade")
            async def event_generator_embed_u():
                yield json.dumps({"reply": templ or ""}, ensure_ascii=False) + "\n"
            return StreamingResponse(event_generator_embed_u(), media_type="application/json")

        # Short-circuit for last estimate summary when data present
        if _is_last_estimate_summary_question(request.message) and request.lastResults:
            import json
            summary = _summarize_last_results(request.lastResults)  # type: ignore[arg-type]
            async def event_generator_last():
                yield json.dumps({"reply": summary}, ensure_ascii=False) + "\n"
            return StreamingResponse(event_generator_last(), media_type="application/json")

        retriever = _get_retriever()
        snippets = retriever.retrieve(request.message, k=4)
        context_block = _format_context_block(snippets)
        page_block = f"[Page] {request.page}" if request.page else ""
        form_block = ""
        if request.formSummary:
            try:
                origin = request.formSummary.get("origin")
                destination = request.formSummary.get("destination")
                vibe = request.formSummary.get("vibe") or request.formSummary.get("selectedVibe")
                start_date = request.formSummary.get("startDate")
                return_date = request.formSummary.get("returnDate")
                form_lines = ["[Form]", f"origin: {origin}", f"destination: {destination}", f"startDate: {start_date}", f"returnDate: {return_date}", f"vibe: {getattr(vibe, 'name', vibe)}"]
                form_block = "\n".join([l for l in form_lines if l is not None])
            except Exception:
                pass

        user_block = ""
        try:
            user_ctx = await build_user_context(request.includeUserContext)  # type: ignore[arg-type]
            if user_ctx:
                user_block = f"[User]\n{user_ctx}"
        except Exception:
            pass

        composed = "\n\n".join([b for b in [context_block, page_block, form_block, user_block] if b])
        if composed:
            user_prompt = f"Context below may help. Use it only if relevant.\n\n{composed}\n\nUser: {request.message}"
        else:
            user_prompt = request.message

        reply = await grok.generate_response(prompt=user_prompt, system_message=SYSTEM_PROMPT, force_json=False)

        async def event_generator():
            import json
            chunk = json.dumps({"reply": reply}, ensure_ascii=False)
            yield chunk + "\n"

        return StreamingResponse(event_generator(), media_type="application/json")
    except Exception as e:
        print(f"Chat stream error: {e}")
        raise HTTPException(status_code=500, detail="Chat stream failed")