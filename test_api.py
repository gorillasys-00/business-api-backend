import requests
import time
import json

base_url = "https://esg-sustainability-score-api.p.rapidapi.com/api/v1"
headers = {
    "x-rapidapi-host": "esg-sustainability-score-api.p.rapidapi.com",
    "x-rapidapi-key": "030b016dbfmsh0e78feb26f5c64ap1de480jsnd387006fe8dd",
    "Content-Type": "application/json"
}

endpoints = [
    {
        "name": "Web抽出 (/web-extract/)",
        "method": "GET",
        "url": f"{base_url}/web-extract/",
        "params": {
            "url": "https://www.nintendo.co.jp/corporate/outline/index.html",
            "target": "会社概要"
        },
        "json": None
    },
    {
        "name": "JSON構造化 (/text-to-json/)",
        "method": "POST",
        "url": f"{base_url}/text-to-json/",
        "params": None,
        "json": {
            "text": "明日の10時から第一会議室でキックオフを行います。参加者は田中と佐藤です。",
            "format_instruction": "日時、場所、参加者を抽出してください"
        }
    },
    {
        "name": "ESG判定 (/esg-score/)",
        "method": "GET",
        "url": f"{base_url}/esg-score/",
        "params": {"company_name": "株式会社リベラAIコンサルティング"},
        "json": None
    },
    {
        "name": "ニッチデータ抽出 (/niche-data/)",
        "method": "GET",
        "url": f"{base_url}/niche-data/",
        "params": {
            "url": "https://www.nintendo.co.jp/corporate/outline/index.html",
            "focus_topic": "この会社の主要な事業拠点について教えて"
        },
        "json": None
    },
    {
        "name": "Webhookテスト (/webhook/register/)",
        "method": "POST",
        "url": f"{base_url}/webhook/register/",
        "params": None,
        "json": {
            "target_url": "https://example.com",
            "callback_url": "https://webhook.site/9b393319-ef9b-494c-8c3a-670726719a55",
            "event_type": "test"
        }
    }
]

print("Starting API Tests...\n")

all_passed = True

for idx, endpoint in enumerate(endpoints):
    print(f"[{idx+1}] Testing: {endpoint['name']}")
    
    try:
        if endpoint["method"] == "GET":
            response = requests.get(endpoint["url"], headers=headers, params=endpoint["params"], allow_redirects=False)
        elif endpoint["method"] == "POST":
            response = requests.post(endpoint["url"], headers=headers, json=endpoint["json"], allow_redirects=False)
        
        status_code = response.status_code
        try:
            resp_text = json.dumps(response.json(), ensure_ascii=False)
        except:
            resp_text = response.text
            
        print(f"  Status Code: {status_code}")
        print(f"  Response: {resp_text[:200]}...")
        
        if status_code != 200:
            all_passed = False
            
    except Exception as e:
        print(f"  Error: {e}")
        all_passed = False
        
    print("-" * 40)
    time.sleep(2)

print("\n--- Test Summary ---")
if all_passed:
    print("All endpoints returned 200 OK without 307 Redirects.")
else:
    print("Some endpoints failed or returned redirects. Check the logs above.")
