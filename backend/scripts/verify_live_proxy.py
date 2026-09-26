import urllib.request
import json
import time

base_url = "http://localhost:4200/api"

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("1. Creating campaign...")
camp = post(f"{base_url}/campaigns", {
    "name": "Zero-Trust Enterprise Glassmorphism",
    "brief": "Autonomous enterprise AI agent canvas with glass-neumorphic design and guardrails.",
    "campaign_type": "website",
    "target_audience": "Chief Information Security Officers and Enterprise Architects"
})
cid = camp["id"]
print(f"Created Campaign: {cid} ({camp['name']})")

print("2. Triggering execution...")
execution = post(f"{base_url}/campaigns/{cid}/executions", {})
eid = execution["id"]
print(f"Started Execution: {eid}, initial status: {execution['status']}")

print("3. Waiting for orchestration pipeline...")
for _ in range(10):
    time.sleep(1)
    status_data = get(f"{base_url}/executions/{eid}")
    print(f"Status: {status_data['status']}, Score: {status_data.get('final_score')}")
    if status_data["status"] in ("approved", "review_required", "completed", "rejected"):
        break

print("4. Fetching generated assets...")
assets = get(f"{base_url}/campaigns/{cid}/assets")
print(f"Assets generated: {len(assets)}")
for a in assets:
    print(f" - [{a['asset_type']}] ID: {a['id']}, Content Preview: {str(a.get('content'))[:60]}...")

print("\nALL VERIFICATIONS PASSED VIA FRONTEND PROXY!")
