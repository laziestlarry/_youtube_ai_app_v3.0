"""
YouTube Upload & Monetization Optimizer
"""
import json
from datetime import datetime, timedelta

class UploadOptimizer:
    def __init__(self):
        self.monetization_checklist = []
    
    def generate_upload_package(self, project_id: str, title: str):
        """Generate complete upload package"""
        
        # SEO-optimized title
        optimized_title = self.optimize_title(title)
        
        # Description with monetization
        description = self.generate_description(title)
        
        # Tags for maximum reach
        tags = self.generate_tags(title)
        
        # Upload timing
        optimal_time = self.get_optimal_upload_time()
        
        # Create upload package
        package = {
            "title": optimized_title,
            "description": description,
            "tags": tags,
            "upload_time": optimal_time,
            "monetization_checklist": self.get_monetization_checklist()
        }
        
        # Save to file
        package_path = f"outputs/scripts/{project_id}_upload_package.json"
        with open(package_path, 'w') as f:
            json.dump(package, f, indent=2)
        
        print(f"📦 Upload package created: {package_path}")
        return package
    
    def optimize_title(self, title: str) -> str:
        """Optimize title for YouTube algorithm"""
        # Add urgency and curiosity
        if "How I Made" in title:
            return title + " (PROOF INSIDE)"
        elif "Secret" in title:
            return title + " - REVEALED"
        else:
            return title + " (WORKS IN 2024)"
    
    def generate_description(self, title: str) -> str:
        """Generate monetization-focused description"""
        return f"""🚀 {title}

In this video, I break down the EXACT method I used to generate serious income online. This isn't theory - these are real results you can replicate.

⏰ TIMESTAMPS:
00:00 - Introduction
00:30 - The Method Revealed  
02:00 - Step-by-Step Process
05:00 - Results & Proof
08:00 - How You Can Start Today

💰 RESOURCES MENTIONED:
🔗 Complete Blueprint: [YOUR AFFILIATE LINK]
🔗 Recommended Tools: [YOUR AFFILIATE LINK]
🔗 Free Training: [YOUR LEAD MAGNET]

📊 CONNECT WITH ME:
• Instagram: @yourusername
• Twitter: @yourusername
• Email: your@email.com

⚠️ DISCLAIMER: Results not typical. Your results may vary.

#MakeMoneyOnline #PassiveIncome #OnlineBusiness #SideHustle #FinancialFreedom

---
This video contains affiliate links. I may earn a commission at no extra cost to you."""
    
    def generate_tags(self, title: str) -> list:
        """Generate SEO tags"""
        base_tags = [
            "make money online",
            "passive income", 
            "online business",
            "side hustle",
            "financial freedom",
            "work from home",
            "internet marketing"
        ]
        
        # Add title-specific tags
        title_words = title.lower().split()
        specific_tags = [word for word in title_words if len(word) > 3]
        
        return base_tags + specific_tags[:10]  # YouTube allows ~15 tags
    
    def get_optimal_upload_time(self) -> str:
        """Get optimal upload time"""
        # Tuesday-Thursday, 2-4 PM EST typically perform best
        optimal_days = ["Tuesday", "Wednesday", "Thursday"]
        optimal_time = "2:00 PM EST"
        
        return f"Best days: {', '.join(optimal_days)} at {optimal_time}"
    
    def get_monetization_checklist(self) -> list:
        """Complete monetization checklist"""
        return [
            "✅ YouTube Partner Program enabled",
            "✅ AdSense account linked", 
            "✅ Affiliate links in description",
            "✅ Lead magnet mentioned",
            "✅ End screen with related videos",
            "✅ Custom thumbnail uploaded",
            "✅ SEO-optimized title and description",
            "✅ Relevant tags added",
            "✅ Cards added for engagement",
            "✅ Community post scheduled",
            "✅ Social media promotion planned",
            "✅ Email list notification sent"
        ]

# Run upload optimizer
if __name__ == "__main__":
    optimizer = UploadOptimizer()
    project_id = input("Enter project ID: ")
    title = input("Enter video title: ")
    
    package = optimizer.generate_upload_package(project_id, title)
    print("\n🎯 NEXT STEPS:")
    print("1. Create thumbnail using AI prompt")
    print("2. Record/generate audio")
    print("3. Create video (screen recording recommended)")
    print("4. Upload to YouTube with generated package")
    print("5. Enable monetization immediately")