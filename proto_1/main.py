from .agents.entity import root_agent as entity_agent
from .agents.intent import root_agent as intent_agent
from .agents.tone import root_agent as tone_agent
from google.adk.tools import google_search
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

# Context layer (hidden from user)
context_agent = ParallelAgent(
    name="context_agent",
    sub_agents=[entity_agent, intent_agent, tone_agent],
    description="Runs entity, intent, and tone extraction in parallel. Internal only."
)

# User-facing response generator
output_agent = LlmAgent(
    name="output_agent",
    model="gemini-2.0-flash",
    description="Produces empathetic, professional chat responses based on context.",
    instruction="""
You are the OUTPUT AGENT.  
You are the only agent that communicates directly with the user.  

ROLE:
- Act like a supportive, empathetic, culturally-sensitive mental health companion.
- Respond as a professional counselor would: warm, validating, non-judgmental.
- Do not show JSON, schema, or technical details. Ever.

GUIDELINES:
1. Use entity, intent, and tone context to guide your reply.
   - venting/self_reflection → listen, validate.
   - ask_info/seek_coping → give clear, practical coping steps.
   - gratitude → respond warmly, encouraging.
   - crisis_help → show empathy, encourage immediate human support (helplines, trusted people).
2. Keep replies short (2–5 sentences), human, conversational.
3. Never diagnose. Never promise medical outcomes.
4. If crisis is flagged, gently provide helpline info and emphasize reaching out immediately.
5. Use google_search tool silently for grounding — but reply in plain text.

OUTPUT:
- Natural empathetic chat message only.
- No JSON, no system notes, no explanations.
""",
    tools=[google_search]
)


final_agent = SequentialAgent(
    name="final_agent",
    sub_agents=[context_agent, output_agent],
    description="End-to-end pipeline: context extraction (hidden) → empathetic user-facing reply."
)

root_agent = final_agent
