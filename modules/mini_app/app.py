"""
YouTube Income Commander Mini - Separate Cash Generation App
Completely independent from main codebase
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import random
from datetime import datetime
import uvicorn

app = FastAPI(title="YouTube Income Commander", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# JIT Monetization Strategies
MONEY_NICHES = {
    "crypto": {"cpm": 12.0, "keywords": ["Bitcoin", "Ethereum", "DeFi", "NFT", "Crypto Trading"]},
    "finance": {"cpm": 15.0, "keywords": ["Investing", "Stocks", "Real Estate", "Passive Income"]},
    "business": {"cpm": 10.0, "keywords": ["Dropshipping", "Amazon FBA", "Online Business", "Side Hustle"]},
    "tech": {"cpm": 8.0, "keywords": ["AI Tools", "Software", "Apps", "Productivity"]},
    "lifestyle": {"cpm": 6.0, "keywords": ["Minimalism", "Self Improvement", "Habits", "Success"]}
}

VIRAL_TEMPLATES = [
    "How I Made ${amount} in {days} Days Using {method}",
    "The {method} Method That Changed My Life",
    "Why Everyone is Using {method} to Make Money",
    "I Tried {method} for 30 Days - Results Will Shock You",
    "{amount} Per Day With This Simple {method} Trick"
]

@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Income Commander</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .revenue { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .idea { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .high-cpm { background: #ff6b6b; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🚀 YouTube Income Commander</h1>
        <div class="revenue">
            <h2>💰 Generate Ideas Worth $500-$5000 Each</h2>
            <p>High-CPM niches • Viral formats • Immediate monetization</p>
        </div>
        <button onclick="generateIdeas()">Generate Money-Making Ideas</button>
        <div id="ideas"></div>
        
        <script>
            async function generateIdeas() {
                const response = await fetch('/generate');
                const data = await response.json();
                document.getElementById('ideas').innerHTML = data.ideas.map(idea => `
                    <div class="idea">
                        <h3>${idea.title}</h3>
                        <span class="high-cpm">HIGH CPM</span>
                        <p>Expected Revenue: <strong>$${idea.revenue}</strong></p>
                        <p>Views: ${idea.views.toLocaleString()} | Category: ${idea.category}</p>
                    </div>
                `).join('');
            }
        </script>
    </body>
    </html>
    """)

@app.get("/generate")
async def generate_ideas():
    """Generate 5 high-revenue video ideas"""
    ideas = []
    
    for _ in range(5):
        niche = random.choice(list(MONEY_NICHES.keys()))
        niche_data = MONEY_NICHES[niche]
        keyword = random.choice(niche_data["keywords"])
        template = random.choice(VIRAL_TEMPLATES)
        
        # Generate realistic numbers
        amount = random.choice(["$1000", "$5000", "$10000", "$25000"])
        days = random.choice(["7", "30", "60", "90"])
        views = random.randint(10000, 100000)
        
        title = template.format(
            amount=amount,
            days=days,
            method=keyword
        )
        
        # Calculate revenue potential
        ad_revenue = (views / 1000) * niche_data["cpm"]
        affiliate_revenue = ad_revenue * 2  # High-converting niches
        total_revenue = round(ad_revenue + affiliate_revenue, 2)
        
        ideas.append({
            "title": title,
            "category": niche,
            "views": views,
            "revenue": total_revenue,
            "cpm": niche_data["cpm"]
        })
    
    # Sort by revenue potential
    ideas.sort(key=lambda x: x["revenue"], reverse=True)
    
    return {
        "ideas": ideas,
        "total_potential": sum(idea["revenue"] for idea in ideas),
        "generated_at": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "app": "youtube-income-commander-mini"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)