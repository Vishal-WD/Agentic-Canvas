import psycopg2
import json

conn = psycopg2.connect("postgresql://ong_user:ong_dev_password@localhost:5432/ong_agentic_canvas")
c = conn.cursor()

print("=" * 60)
print("ACTUAL POSTGRESQL (DOCKER) OUTPUTS INSPECTED")
print("=" * 60)

# 1. Latest Campaign
c.execute("SELECT id, name, brief, campaign_type, target_audience, status FROM campaigns ORDER BY created_at DESC LIMIT 1")
camp = c.fetchone()
if camp:
    cid, name, brief, ctype, audience, status = camp
    print(f"\n[1] LATEST CAMPAIGN RECORD IN POSTGRESQL:")
    print(f"    - ID: {cid}")
    print(f"    - Name: {name}")
    print(f"    - Type: {ctype}")
    print(f"    - Target Audience: {audience}")
    print(f"    - Brief: {brief}")
    print(f"    - Status: {status}")

    # 2. Latest Execution
    c.execute("SELECT id, status, final_score, current_state FROM executions WHERE campaign_id = %s ORDER BY started_at DESC NULLS LAST LIMIT 1", (str(cid),))
    exe = c.fetchone()
    if exe:
        eid, estatus, score, state = exe
        print(f"\n[2] EXECUTION RECORD IN POSTGRESQL:")
        print(f"    - ID: {eid}")
        print(f"    - Status: {estatus}")
        print(f"    - State: {state}")
        print(f"    - Final Compliance Score: {score}")

        # 3. Agent Runs
        c.execute("SELECT agent_name, status, latency_ms, output_data FROM agent_runs WHERE execution_id = %s ORDER BY created_at ASC", (str(eid),))
        runs = c.fetchall()
        print(f"\n[3] AGENT RUNS RECORDED ({len(runs)} agents executed):")
        for rname, rstat, rlat, rout in runs:
            print(f"    • Agent: {rname:<20} | Status: {rstat:<10} | Latency: {rlat:.2f}ms")

        # 4. Generated Assets
        c.execute("SELECT asset_type, content FROM generated_assets WHERE campaign_id = %s", (str(cid),))
        assets = c.fetchall()
        print(f"\n[4] PERSISTED ASSETS IN POSTGRESQL ({len(assets)} assets):")
        for atype, acontent in assets:
            print(f"\n    --- ASSET TYPE: {atype.upper()} ---")
            print(json.dumps(acontent, indent=6))

        # 5. Guardrail Results
        c.execute("SELECT overall_score, status, category_scores, critical_violation FROM guardrail_results WHERE execution_id = %s", (str(eid),))
        gr = c.fetchone()
        if gr:
            fscore, gstatus, cats, crit = gr
            print(f"\n[5] GUARDRAIL EVALUATION IN POSTGRESQL:")
            print(f"    - Final Score: {fscore}")
            print(f"    - Verdict: {gstatus}")
            print(f"    - Critical Violation: {crit}")
            print(f"    - Category Scores: {json.dumps(cats, indent=6)}")

conn.close()
