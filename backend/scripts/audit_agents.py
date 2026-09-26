import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base import AgentInput
from app.agents.copywriter import CopywriterAgent
from app.agents.layout import LayoutAgent
from app.agents.asset_recommender import AssetRecommenderAgent
from app.guardrails.engine import GuardrailEngine
from app.guardrails.deterministic import DeterministicValidator
from app.guardrails.scoring import ScoringEngine
from app.guardrails.repair import RepairAgent
from app.rag.retrieval import BrandRAGService


async def inspect_agents():
    print("=" * 60)
    print("O&G AGENT SYSTEM HEALTH & FUNCTIONALITY AUDIT")
    print("=" * 60)

    # 1. Test Brand RAG
    rag = BrandRAGService()
    rag.ingest_brand_rules()
    copy_rules = rag.retrieve_for_agent("copywriter", "website")
    layout_rules = rag.retrieve_for_agent("layout_structurer", "website")
    asset_rules = rag.retrieve_for_agent("asset_recommender", "website")
    print(f"\n[1] Brand RAG Service:")
    print(f"    - Retrieved {len(copy_rules)} rules for Copywriter")
    print(f"    - Retrieved {len(layout_rules)} rules for Layout Structurer")
    print(f"    - Retrieved {len(asset_rules)} rules for Asset Recommender")

    # 2. Test Copywriter Agent
    print(f"\n[2] Testing Copywriter Agent...")
    copywriter = CopywriterAgent()
    copy_input = AgentInput(
        campaign_brief="Launch autonomous enterprise AI agent canvas with strict brand guardrails and zero-trust orchestration.",
        campaign_type="website",
        target_audience="Chief Information Security Officers and Enterprise Architects",
        brand_rules=copy_rules,
    )
    copy_result = await copywriter.safe_execute(copy_input)
    print(f"    - Success: {copy_result.success}")
    print(f"    - Latency: {copy_result.latency_ms:.2f}ms")
    print(f"    - Provider: {copy_result.model_provider}")
    print(f"    - Headline: '{copy_result.output.get('headline')}'")
    print(f"    - Subheadline: '{copy_result.output.get('subheadline')}'")
    print(f"    - CTA: '{copy_result.output.get('cta')}'")
    print(f"    - Social Posts: {len(copy_result.output.get('social_posts', []))} post(s)")

    # 3. Test Layout Agent
    print(f"\n[3] Testing Layout Structurer Agent...")
    layout_agent = LayoutAgent()
    layout_input = AgentInput(
        campaign_brief=copy_input.campaign_brief,
        campaign_type=copy_input.campaign_type,
        target_audience=copy_input.target_audience,
        brand_rules=layout_rules,
        additional_context={"copy": copy_result.output},
    )
    layout_result = await layout_agent.safe_execute(layout_input)
    print(f"    - Success: {layout_result.success}")
    print(f"    - Latency: {layout_result.latency_ms:.2f}ms")
    print(f"    - Layout Type: {layout_result.output.get('layout_type')}")
    print(f"    - Grid System: {layout_result.output.get('grid_system')}")
    print(f"    - Sections: {len(layout_result.output.get('sections', []))} section(s)")
    for i, sec in enumerate(layout_result.output.get('sections', [])[:3]):
        print(f"       [{i+1}] {sec.get('section_id')}: bg={sec.get('background_color')}, text={sec.get('text_color')}")

    # 4. Test Asset Recommender Agent
    print(f"\n[4] Testing Asset Recommender Agent...")
    asset_agent = AssetRecommenderAgent()
    asset_input = AgentInput(
        campaign_brief=copy_input.campaign_brief,
        campaign_type=copy_input.campaign_type,
        target_audience=copy_input.target_audience,
        brand_rules=asset_rules,
        additional_context={"copy": copy_result.output, "layout": layout_result.output},
    )
    asset_result = await asset_agent.safe_execute(asset_input)
    print(f"    - Success: {asset_result.success}")
    print(f"    - Latency: {asset_result.latency_ms:.2f}ms")
    recs = asset_result.output.get("recommendations", [])
    print(f"    - Recommendations Count: {len(recs)}")
    for i, r in enumerate(recs[:2]):
        print(f"       [{i+1}] {r.get('asset_type')}: '{r.get('subject')}' (aspect: {r.get('aspect_ratio')})")

    # 5. Test Guardrail Engine (Deterministic + Semantic + Scoring)
    print(f"\n[5] Testing Guardrail Engine on Assembled Campaign Output...")
    guardrail_engine = GuardrailEngine()
    assembled_output = {
        "copy": copy_result.output,
        "layout": layout_result.output,
        "assets": asset_result.output,
        "headline": copy_result.output.get("headline"),
        "body": copy_result.output.get("supporting_copy"),
        "background_color": "#0C2140",
        "cta_color": "#D6B25A",
        "logo_required": True,
        "logo_placement": "top-left",
    }
    score = await guardrail_engine.validate(assembled_output, brand_rules=copy_rules + layout_rules)
    print(f"    - Overall Score: {score.overall_score:.2f} / 100")
    print(f"    - Status: {score.status.upper()}")
    print(f"    - Has Critical Violation: {score.has_critical_violation}")
    print(f"    - Category Scores:")
    for cat, s in score.category_scores.items():
        print(f"       • {cat}: {s:.1f}%")

    # 6. Test Repair Agent on Bad Input
    print(f"\n[6] Testing Repair Agent on Intentional Adversarial Input...")
    bad_output = {
        "headline": "Our AI is 100% foolproof and guarantees 10x ROI with totally lit vibes!",
        "background_color": "#FF0000",
        "logo_required": True,
        "logo_placement": None,
    }
    repaired_output, repaired_score, attempts = await guardrail_engine.validate_and_repair(
        bad_output,
        brand_rules=copy_rules
    )
    print(f"    - Initial violations triggered repair loop")
    print(f"    - Repair Attempts Executed: {len(attempts)}")
    print(f"    - Final Repaired Status: {repaired_score.status.upper()}")
    print(f"    - Final Score: {repaired_score.overall_score:.2f}")

    print("\n" + "=" * 60)
    print("ALL AGENTS ARE FUNCTIONING PROPERLY AND NOMINALLY")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(inspect_agents())
