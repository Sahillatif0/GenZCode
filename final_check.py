import requests
import json

url = "http://localhost:5000/pipeline"
code = """
lowkey score: num = 85;
sus (score >= 60) {
    spill_tea("Passed! No cap.");
}
"""
payload = {"code": code}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = response.json()
    opt_stage = next(s for s in data['stages'] if s['name'] == 'optimizer')
    print("--- Optimized IR ---")
    print(opt_stage['optimized_ir'])
    print("\n--- Report ---")
    print(opt_stage['optimization_report'])
except Exception as e:
    print(f"Error: {e}")
