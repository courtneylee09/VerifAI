#!/usr/bin/env python3
"""Monitor Railway deployment status."""

import urllib.request
import json
import time
import sys

SERVICE_URL = "https://verifai-production.up.railway.app"

def check_health():
    try:
        r = urllib.request.urlopen(f"{SERVICE_URL}/health", timeout=5)
        return r.status == 200
    except Exception as e:
        return False

def check_metrics():
    try:
        r = urllib.request.urlopen(f"{SERVICE_URL}/metrics/economics", timeout=5)
        data = json.loads(r.read())
        return data
    except Exception as e:
        return None

print("Checking VerifAI deployment status...\n")

max_attempts = 12  # 60 seconds with 5s intervals
attempt = 0

while attempt < max_attempts:
    attempt += 1
    print(f"[Attempt {attempt}/{max_attempts}] Checking service...", end=" ")
    
    if check_health():
        print("✅ Service responding")
        print("\nFetching metrics...", end=" ")
        
        metrics = check_metrics()
        if metrics:
            print("✅ Metrics endpoint live!")
            print("\n" + "="*70)
            print("DEPLOYMENT STATUS: ✅ LIVE TO THE WORLD")
            print("="*70)
            print(f"\n📊 Profit Summary:")
            print(f"   Total Requests: {metrics['metrics']['total_requests']}")
            print(f"   Revenue: ${metrics['metrics']['total_revenue_usd']:.4f}")
            print(f"   Costs: ${metrics['metrics']['total_cost_usd']:.6f}")
            print(f"   Profit: ${metrics['metrics']['total_profit_usd']:.4f}")
            print(f"   Margin: {metrics['metrics']['avg_margin_pct']:.2f}%")
            print(f"\n🌐 Public URL: {SERVICE_URL}")
            print(f"   /verify - Claim verification (requires x402 payment)")
            print(f"   /metrics/economics - Profit summary")
            print(f"   /metrics/logs?limit=20 - Recent requests with economics")
            print(f"   /health - Service health check")
            print("\n" + "="*70)
            sys.exit(0)
        else:
            print("⏳ Metrics still loading...")
    else:
        print("⏳ Service starting...")
    
    if attempt < max_attempts:
        time.sleep(5)

print("\n❌ Service still not responding after 60 seconds")
print("   Check Railway dashboard for deployment logs")
print(f"   URL: https://railway.app/project/[project-id]")
