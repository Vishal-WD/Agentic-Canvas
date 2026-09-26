import sqlite3
import json

conn = sqlite3.connect("ong_canvas.db")
c = conn.cursor()

print("=" * 60)
print("ACTUAL DATABASE OUTPUTS INSPECTED")
print("=" * 60)

# 1. Latest Campaign
c.execute("SELECT id, name, brief, campaign_type, target_audience, status FROM campaigns ORDER BY created_at DESC LIMIT 1")
camp = c.fetchone()
if camp:
    cid, name, brief, ctype, audience, status = camp
    print(f"\n[1] LATEST CAMPAIGN RECORD:")
    print(f"    - ID: {cid}")
    print(f"    - Name: {name}")
    print(f"    - Type: {ctype}")
    print(f"    - Target Audience: {audience}")
    print(f"    - Brief: {brief}")
    print(f"    - Status: {status}")

    # 2. Latest Execution
    c.execute("SELECT id, status, final_score, current_state FROM executions WHERE campaign_id = ? ORDER BY id DESC LIMIT 1", (cid,))
    exe = c.fetchone()
    if exe:
        eid, estatus, score, state = exe
        print(f"\n[2] EXECUTION RECORD:")
        print(f"    - ID: {eid}")
        print(f"    - Status: {estatus}")
        print(f"    - State: {state}")
        print(f"    - Final Compliance Score: {score}")

        # 3. Agent Runs
        c.execute("SELECT agent_name, status, latency_ms, output_data FROM agent_runs WHERE execution_id = ? ORDER BY created_at ASC", (eid,))
        runs = c.fetchall()
        print(f"\n[3] AGENT RUNS ({len(runs)} agents executed):")
        for rname, rstat, rlat, rout in runs:
            print(f"\n    --- AGENT: {rname.upper()} (Status: {rstat}, Latency: {rlat}ms) ---")
            try:
                out_obj = json.loads(rout) if rout else {}
                print(json.dumps(out_obj, indent=6))
            except Exception:
                print(rout[:300])

        # 4. Generated Assets
        c.execute("SELECT asset_type, content FROM generated_assets WHERE campaign_id = ?", (cid,))
        assets = c.fetchall()
        print(f"\n[4] PERSISTED GENERATED ASSETS ({len(assets)} assets):")
        for atype, acontent in assets:
            print(f"\n    --- ASSET TYPE: {atype.upper()} ---")
            try:
                c_obj = json.loads(acontent) if acontent else {}
                print(json.dumps(c_obj, indent=6))
            except Exception:
                print(acontent[:300])

        # 5. Guardrail Results
        c.execute("SELECT deterministic_score, semantic_score, final_score, status, category_scores, violations_count FROM guardrail_results WHERE execution_id = ?", (eid,))
        gr = c.fetchone()
        if gr:
            dscore, sscore, fscore, gstatus, cats, vcount = gr
            print(f"\n[5] GUARDRAIL EVALUATION RECORD:")
            print(f"    - Deterministic Score: {dscore}")
            print(f"    - Semantic Score: {sscore}")
            print(f"    - Final Score: {fscore}")
            print(f"    - Verdict: {gstatus}")
            print(f"    - Category Scores: {cats}")
            print(f"    - Violations Count: {vcount}")

conn.close()
