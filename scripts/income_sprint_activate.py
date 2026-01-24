#!/usr/bin/env python3
"""
Income Sprint Activation - Earliest Revenue Suppliers Launch

Activates all income channels simultaneously:
1. Shopier products with flash sale
2. Social media content deployment
3. Community engagement push
4. Email capture setup

Target: First $500 within 48-72 hours
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗███╗   ██╗ ██████╗ ██████╗ ███╗   ███╗███████╗                          ║
║   ██║████╗  ██║██╔════╝██╔═══██╗████╗ ████║██╔════╝                          ║
║   ██║██╔██╗ ██║██║     ██║   ██║██╔████╔██║█████╗                            ║
║   ██║██║╚██╗██║██║     ██║   ██║██║╚██╔╝██║██╔══╝                            ║
║   ██║██║ ╚████║╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗                          ║
║   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝                          ║
║                                                                              ║
║   ███████╗██████╗ ██████╗ ██╗███╗   ██╗████████╗                             ║
║   ██╔════╝██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝                             ║
║   ███████╗██████╔╝██████╔╝██║██╔██╗ ██║   ██║                                ║
║   ╚════██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║                                ║
║   ███████║██║     ██║  ██║██║██║ ╚████║   ██║                                ║
║   ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝                                ║
║                                                                              ║
║              EARLIEST INCOME SUPPLIERS ACTIVATION                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


class IncomeSprintActivator:
    """Activates all income channels for immediate revenue generation"""
    
    def __init__(self):
        self.shopier_token = os.getenv("SHOPIER_PERSONAL_ACCESS_TOKEN")
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "channels": {},
            "total_potential_revenue": 0,
            "actions_taken": [],
            "next_steps": [],
        }
    
    def run_full_sprint(self) -> Dict[str, Any]:
        """Execute full income activation sprint"""
        print("\n" + "=" * 60)
        print("  PHASE 1: SHOPIER PRODUCT ACTIVATION")
        print("=" * 60)
        self._activate_shopier()
        
        print("\n" + "=" * 60)
        print("  PHASE 2: SOCIAL CONTENT DEPLOYMENT")
        print("=" * 60)
        self._deploy_social_content()
        
        print("\n" + "=" * 60)
        print("  PHASE 3: COMMUNITY ENGAGEMENT LAUNCH")
        print("=" * 60)
        self._launch_community_engagement()
        
        print("\n" + "=" * 60)
        print("  PHASE 4: LEAD CAPTURE SETUP")
        print("=" * 60)
        self._setup_lead_capture()
        
        print("\n" + "=" * 60)
        print("  PHASE 5: FLASH SALE CONFIGURATION")
        print("=" * 60)
        self._configure_flash_sale()
        
        self._generate_sprint_report()
        
        return self.results
    
    def _activate_shopier(self):
        """Activate and verify Shopier products"""
        if not self.shopier_token:
            print("  ⚠️  Shopier token not found")
            return
        
        try:
            resp = requests.get(
                "https://api.shopier.com/v1/products",
                headers={"Authorization": f"Bearer {self.shopier_token}"},
                timeout=30
            )
            
            if resp.status_code != 200:
                print(f"  ❌ API error: {resp.status_code}")
                return
            
            products = resp.json()
            active_products = [p for p in products if p.get("stockStatus") == "inStock"]
            
            print(f"  ✅ Connected to Shopier")
            print(f"  📦 Total Products: {len(products)}")
            print(f"  🟢 Active (In Stock): {len(active_products)}")
            
            # Calculate potential revenue
            total_value = sum(float(p.get("priceData", {}).get("price", 0)) for p in active_products)
            print(f"  💰 Catalog Value: {total_value:,.0f} TRY")
            
            # List top products for sprint
            print("\n  TOP REVENUE TARGETS:")
            sorted_products = sorted(
                active_products,
                key=lambda x: float(x.get("priceData", {}).get("price", 0)),
                reverse=True
            )[:5]
            
            for i, p in enumerate(sorted_products, 1):
                price = float(p.get("priceData", {}).get("price", 0))
                print(f"    {i}. {p['title'][:40]} - {price:,.0f} TRY")
                print(f"       URL: {p['url']}")
            
            self.results["channels"]["shopier"] = {
                "status": "active",
                "products": len(active_products),
                "catalog_value_try": total_value,
                "top_products": [
                    {"title": p["title"], "price": float(p.get("priceData", {}).get("price", 0)), "url": p["url"]}
                    for p in sorted_products
                ],
            }
            self.results["actions_taken"].append("Shopier catalog verified and ready")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def _deploy_social_content(self):
        """Prepare social content for deployment"""
        social_dir = self.project_root / "marketing_outputs" / "social_posts"
        
        if not social_dir.exists():
            print("  ⚠️  Social content directory not found")
            return
        
        # Find latest content files
        content_files = list(social_dir.glob("*.txt"))
        
        print(f"  📄 Content Files Ready: {len(content_files)}")
        
        # Generate fresh launch content
        launch_content = self._generate_launch_content()
        
        # Save to file
        output_file = social_dir / f"SPRINT_LAUNCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, "w") as f:
            f.write(launch_content)
        
        print(f"  ✅ Launch content saved: {output_file.name}")
        
        # Display content for immediate posting
        print("\n  IMMEDIATE POST CONTENT:")
        print("  " + "-" * 56)
        
        platforms = {
            "linkedin": "https://www.linkedin.com/in/lazy-larry-344631373/",
            "twitter": "https://x.com/lazylarries",
            "facebook": "https://www.facebook.com/profile.php?id=61578065763242",
        }
        
        for platform, url in platforms.items():
            print(f"\n  📍 {platform.upper()}: {url}")
        
        self.results["channels"]["social"] = {
            "status": "content_ready",
            "platforms": list(platforms.keys()),
            "content_file": str(output_file),
        }
        self.results["actions_taken"].append("Social launch content generated")
        self.results["next_steps"].append("Post content to LinkedIn, Twitter, Facebook")
    
    def _generate_launch_content(self) -> str:
        """Generate sprint launch content"""
        return """
================================================================================
INCOME SPRINT - LAUNCH CONTENT
================================================================================
Generated: {timestamp}

================================================================================
LINKEDIN POST
================================================================================

🚀 48-HOUR FLASH SALE - Everything 20% OFF

I've been building automation systems for solopreneurs for the past year.

Today I'm doing something I've never done before:

Opening up my entire product vault at 20% off.

What's inside:
→ Fiverr AI Services Kit (launch your AI gig in 1 day)
→ Automation SOP Vault (50+ ready-to-use processes)
→ Notion Revenue Dashboard (track everything in one place)
→ Reddit Launch Playbook (organic traffic without ads)
→ Discord Community Kit (build engaged communities)

Why am I doing this?

Because I believe these systems should be in the hands of people who will actually use them - not sitting in my Google Drive.

48 hours. Then prices go back to normal.

Link in comments 👇

#Automation #PassiveIncome #Solopreneur #FlashSale

================================================================================
TWITTER POST
================================================================================

🚀 48-HOUR FLASH SALE

Everything in my product vault is 20% off.

• Fiverr AI Kit
• Automation SOPs
• Notion Dashboard
• Reddit Playbook
• Discord Kit

48 hours only.

Link below 🧵

================================================================================
FACEBOOK POST
================================================================================

🎉 I'm doing something crazy...

48-HOUR FLASH SALE on my entire product collection.

I've spent the past year building automation systems, templates, and playbooks.

Now I'm opening up everything at 20% off.

Perfect if you've been thinking about:
✅ Starting a side hustle
✅ Automating your business
✅ Building passive income
✅ Launching on Fiverr/Etsy/Gumroad

Comment "LAZY" and I'll send you the link!

================================================================================
PRODUCT LINKS (Add to posts)
================================================================================

Fiverr AI Kit: https://www.shopier.com/43225400
Blog SEO Sprint: https://www.shopier.com/42801172
Gumroad Accelerator: https://www.shopier.com/42801170
Discord Ops Kit: https://www.shopier.com/42801169
Reddit Launch Plan: https://www.shopier.com/42801168
Notion Dashboard: https://www.shopier.com/42801167
Automation SOP Vault: https://www.shopier.com/42801166
Hybrid Income Stack: https://www.shopier.com/42801165

================================================================================
""".format(timestamp=datetime.utcnow().isoformat())
    
    def _launch_community_engagement(self):
        """Prepare community engagement actions"""
        communities = [
            {
                "name": "Indie Hackers",
                "url": "https://www.indiehackers.com/",
                "action": "Post introduction + share flash sale",
                "priority": 1,
            },
            {
                "name": "r/Entrepreneur",
                "url": "https://reddit.com/r/Entrepreneur",
                "action": "Value comment (no direct selling yet)",
                "priority": 1,
            },
            {
                "name": "r/passive_income",
                "url": "https://reddit.com/r/passive_income",
                "action": "Share automation strategy",
                "priority": 2,
            },
            {
                "name": "r/SideProject",
                "url": "https://reddit.com/r/SideProject",
                "action": "Launch announcement",
                "priority": 2,
            },
        ]
        
        print("  COMMUNITY TARGETS:")
        for c in communities:
            print(f"    P{c['priority']} | {c['name']}")
            print(f"       Action: {c['action']}")
            print(f"       URL: {c['url']}")
        
        # Generate community intro post
        intro_post = self._generate_community_intro()
        
        intro_file = self.project_root / "marketing_outputs" / "social_posts" / f"COMMUNITY_INTRO_{datetime.utcnow().strftime('%Y%m%d')}.txt"
        with open(intro_file, "w") as f:
            f.write(intro_post)
        
        print(f"\n  ✅ Community intro saved: {intro_file.name}")
        
        self.results["channels"]["communities"] = {
            "status": "ready",
            "targets": communities,
            "intro_file": str(intro_file),
        }
        self.results["next_steps"].append("Join Indie Hackers and post introduction")
        self.results["next_steps"].append("Engage in r/Entrepreneur (value-first)")
    
    def _generate_community_intro(self) -> str:
        """Generate community introduction post"""
        return """
================================================================================
COMMUNITY INTRODUCTION POST
================================================================================

FOR: Indie Hackers, Reddit, Facebook Groups

================================================================================
INDIE HACKERS VERSION
================================================================================

Hey IH! 👋

I'm Larry (yes, Lazy Larry - I own it).

Quick background:
- Spent years grinding 80-hour weeks
- Discovered automation changed everything
- Now work ~20 hours/week with better results

What I'm building:
• AutonomaX - AI business operating system
• Zen Collections - Digital art products
• Various automation templates and playbooks

Currently running a 48-hour sprint to hit my first $500 from digital products.

Here to learn from this community and share what's working.

Questions I'd love input on:
1. What's your best-converting lead magnet format?
2. How do you balance building vs. marketing?

What's everyone working on this week?

================================================================================
REDDIT VERSION (r/Entrepreneur)
================================================================================

[Value Post - No Direct Selling]

Title: How I automated 80% of my solopreneur tasks (breakdown inside)

After years of manual work, I finally mapped out every repetitive task and automated them.

Here's what I automated:
- Customer onboarding (email sequences)
- Order fulfillment (digital delivery)
- Social posting (scheduled content)
- Lead capture (automated follow-up)
- Revenue tracking (dashboard updates)

Time saved: ~30 hours/week

The key wasn't fancy tools - it was documenting processes first, THEN automating.

Happy to share specific workflows if anyone's interested.

What tasks are eating most of your time right now?

================================================================================
"""
    
    def _setup_lead_capture(self):
        """Setup lead capture mechanisms"""
        print("  LEAD CAPTURE SETUP:")
        
        lead_magnets = [
            {
                "name": "Automation Starter Kit",
                "type": "Checklist PDF",
                "hook": "10 automations every solopreneur needs",
                "status": "to_create",
            },
            {
                "name": "7-Day Lazy Launch",
                "type": "Email Course",
                "hook": "Launch your first digital product this week",
                "status": "to_create",
            },
        ]
        
        for lm in lead_magnets:
            print(f"    📄 {lm['name']} ({lm['type']})")
            print(f"       Hook: {lm['hook']}")
            print(f"       Status: {lm['status']}")
        
        # For now, use direct product links as capture
        print("\n  IMMEDIATE CAPTURE METHOD:")
        print("    Using product pages as landing pages")
        print("    Add 'DM me LAZY for discount code' CTA to posts")
        
        self.results["channels"]["lead_capture"] = {
            "status": "basic",
            "method": "DM-based discount codes",
            "planned_magnets": lead_magnets,
        }
        self.results["next_steps"].append("Create simple lead magnet (checklist)")
    
    def _configure_flash_sale(self):
        """Configure flash sale parameters"""
        print("  FLASH SALE CONFIGURATION:")
        
        sale_config = {
            "discount": "20%",
            "duration": "48 hours",
            "start": datetime.utcnow().isoformat(),
            "end": (datetime.utcnow() + timedelta(hours=48)).isoformat(),
            "products": "all",
            "code": "LAZY20",
            "urgency_messages": [
                "48 hours only",
                "Sale ends tomorrow",
                "Last chance - 6 hours left",
            ],
        }
        
        print(f"    Discount: {sale_config['discount']}")
        print(f"    Duration: {sale_config['duration']}")
        print(f"    Code: {sale_config['code']}")
        print(f"    Start: {sale_config['start'][:16]}")
        print(f"    End: {sale_config['end'][:16]}")
        
        # Note: Shopier doesn't have API for discount codes
        # Discount must be applied manually or use manual pricing
        print("\n  ⚠️  ACTION REQUIRED:")
        print("    1. Go to Shopier seller dashboard")
        print("    2. Create discount code 'LAZY20' for 20% off")
        print("    3. Or manually reduce prices for 48 hours")
        
        self.results["channels"]["flash_sale"] = sale_config
        self.results["next_steps"].insert(0, "Configure LAZY20 discount code in Shopier")
    
    def _generate_sprint_report(self):
        """Generate final sprint activation report"""
        print("\n" + "=" * 60)
        print("  INCOME SPRINT ACTIVATION REPORT")
        print("=" * 60)
        
        print(f"\n  Timestamp: {self.results['timestamp']}")
        print(f"\n  CHANNELS ACTIVATED:")
        
        for channel, data in self.results["channels"].items():
            status = data.get("status", "unknown")
            icon = "✅" if status in ["active", "ready", "content_ready"] else "⏳"
            print(f"    {icon} {channel.upper()}: {status}")
        
        print(f"\n  ACTIONS TAKEN: {len(self.results['actions_taken'])}")
        for action in self.results["actions_taken"]:
            print(f"    ✓ {action}")
        
        print(f"\n  IMMEDIATE NEXT STEPS:")
        for i, step in enumerate(self.results["next_steps"], 1):
            print(f"    {i}. {step}")
        
        # Calculate revenue target
        shopier_data = self.results["channels"].get("shopier", {})
        if shopier_data.get("top_products"):
            avg_price = sum(p["price"] for p in shopier_data["top_products"]) / len(shopier_data["top_products"])
            # Assume 35 TRY = 1 USD roughly
            target_orders = 5  # To hit $500 target
            print(f"\n  REVENUE TARGET:")
            print(f"    Target: $500 USD (~17,500 TRY)")
            print(f"    Avg Product Price: {avg_price:,.0f} TRY")
            print(f"    Orders Needed: ~{int(17500 / avg_price)} orders")
        
        # Save report
        report_file = self.project_root / "marketing_outputs" / f"income_sprint_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n  📄 Report saved: {report_file.name}")


def main():
    print_banner()
    
    activator = IncomeSprintActivator()
    results = activator.run_full_sprint()
    
    print("\n" + "=" * 60)
    print("  🚀 SPRINT ACTIVATION COMPLETE")
    print("=" * 60)
    print("""
  YOUR IMMEDIATE ACTIONS (Do Now):
  
  1. 🛒 SHOPIER: Create discount code LAZY20 (20% off)
     https://www.shopier.com/seller/discounts
  
  2. 📱 LINKEDIN: Post flash sale announcement
     https://www.linkedin.com/in/lazy-larry-344631373/
  
  3. 🐦 TWITTER: Post flash sale thread
     https://x.com/lazylarries
  
  4. 📘 FACEBOOK: Post with "Comment LAZY" CTA
     https://www.facebook.com/profile.php?id=61578065763242
  
  5. 🌐 INDIE HACKERS: Join and post introduction
     https://www.indiehackers.com/
  
  Content files ready in: marketing_outputs/social_posts/
  
  ⏱️  TIMER STARTS NOW - 48 HOURS
""")


if __name__ == "__main__":
    main()
