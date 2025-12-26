"""
Complete Sequential YouTube Production Pipeline
Handles: Script → Audio → Thumbnail → Video → Upload Package
"""
import os
import json
import sqlite3
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import uuid
import time

class CompleteYouTubePipeline:
    def __init__(self):
        self.project_id = None
        self.project_data = {}
        self.setup_directories()
        
    def setup_directories(self):
        """Create all necessary directories"""
        dirs = ['outputs/scripts', 'outputs/audio', 'outputs/thumbnails', 
                'outputs/videos', 'outputs/upload_packages']
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        print("📁 Directories created")

    def run_complete_pipeline(self, title: str, niche: str, revenue_potential: float):
        """Run the complete pipeline in sequence"""
        self.project_id = str(uuid.uuid4())[:8]
        self.project_data = {
            'title': title,
            'niche': niche,
            'revenue_potential': revenue_potential,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"🚀 Starting Complete Pipeline for Project: {self.project_id}")
        print(f"📝 Title: {title}")
        print(f"💰 Revenue Potential: ${revenue_potential}")
        print("="*60)
        
        try:
            # Step 1: Generate Script
            print("\n📝 STEP 1: GENERATING SCRIPT...")
            script_path = self.generate_script()
            print(f"✅ Script created: {script_path}")
            
            # Step 2: Create Audio
            print("\n🎵 STEP 2: CREATING AUDIO...")
            audio_path = self.create_audio(script_path)
            print(f"✅ Audio created: {audio_path}")
            
            # Step 3: Generate Thumbnail
            print("\n🎨 STEP 3: GENERATING THUMBNAIL...")
            thumbnail_path = self.create_thumbnail()
            print(f"✅ Thumbnail guide created: {thumbnail_path}")
            
            # Step 4: Create Video
            print("\n🎬 STEP 4: CREATING VIDEO...")
            video_path = self.create_video(audio_path, thumbnail_path)
            print(f"✅ Video created: {video_path}")
            
            # Step 5: Generate Upload Package
            print("\n📤 STEP 5: GENERATING UPLOAD PACKAGE...")
            upload_package = self.create_upload_package()
            print(f"✅ Upload package created: {upload_package}")
            
            # Step 6: Save to Database
            print("\n💾 STEP 6: SAVING TO DATABASE...")
            self.save_to_database()
            print("✅ Project saved to database")
            
            # Final Summary
            self.print_completion_summary()
            
            return {
                'success': True,
                'project_id': self.project_id,
                'files': {
                    'script': script_path,
                    'audio': audio_path,
                    'thumbnail': thumbnail_path,
                    'video': video_path,
                    'upload_package': upload_package
                }
            }
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def generate_script(self):
        """Step 1: Generate complete video script"""
        script_templates = {
            "crypto": """
🎬 INTRO (0-15s):
"What's up everyone! Today I'm revealing the {method} that helped me make {amount} in just {timeframe}. 
This is NOT financial advice, but the results speak for themselves. Let's dive in!"

🎯 HOOK (15-30s):
"Before we start, if you want more money-making strategies like this, smash that subscribe button and ring the notification bell!"

📊 MAIN CONTENT (30s-8min):
"Here's exactly what I did step by step:

Step 1: I discovered this {method} strategy that 99% of people don't know about...
[Show specific examples and proof]

Step 2: I implemented it using these exact tools...
[Demonstrate the tools and process]

Step 3: The results started coming in within {timeframe}...
[Display earnings screenshots and analytics]

The key is consistency and following this exact system I'm about to share with you."

💰 MONETIZATION (8-9min):
"If you want the complete blueprint I used, check out the first link in the description. 
It's the exact same system that generated these results."

🔔 OUTRO (9-10min):
"Drop a comment below with your biggest takeaway, subscribe for more money-making content, 
and I'll see you in the next video!"
            """,
            
            "finance": """
🎬 INTRO (0-15s):
"In this video, I'm breaking down exactly how I generated {amount} using {method}. 
This changed everything for me financially, and it can do the same for you."

🎯 HOOK (15-30s):
"Make sure to subscribe because I share these money-making strategies every week!"

📊 MAIN CONTENT (30s-8min):
"Here's the complete breakdown:

The Problem: Most people struggle with building wealth because they don't know this...

The Solution: I discovered {method} and here's exactly how it works...
[Detailed explanation with real examples]

The Results: Within {timeframe}, I was able to generate {amount}...
[Show proof, bank statements, analytics]

The System: Here's the exact process you can follow starting today..."

💰 CALL TO ACTION (8-9min):
"Everything you need to get started is linked in the description below."

🔔 OUTRO (9-10min):
"What's your experience with {method}? Let me know in the comments, 
and don't forget to subscribe for more financial content!"
            """
        }
        
        # Extract variables from title
        import re
        amount_match = re.search(r'\$[\d,]+', self.project_data['title'])
        amount = amount_match.group() if amount_match else "$5,000"
        
        timeframe_match = re.search(r'\d+\s*(days?|weeks?|months?)', self.project_data['title'].lower())
        timeframe = timeframe_match.group() if timeframe_match else "30 days"
        
        method = self.project_data['title'].split()[-2] if len(self.project_data['title'].split()) > 2 else self.project_data['niche']
        
        template = script_templates.get(self.project_data['niche'].lower(), script_templates["finance"])
        
        script = template.format(
            method=method,
            amount=amount,
            timeframe=timeframe
        )
        
        # Save script
        script_path = f"outputs/scripts/{self.project_id}_script.txt"
        with open(script_path, 'w') as f:
            f.write(f"PROJECT: {self.project_id}\n")
            f.write(f"TITLE: {self.project_data['title']}\n")
            f.write(f"NICHE: {self.project_data['niche']}\n")
            f.write(f"REVENUE POTENTIAL: ${self.project_data['revenue_potential']}\n")
            f.write("="*60 + "\n\n")
            f.write(script)
            f.write("\n\n" + "="*60)
            f.write("\n🎯 SCRIPT NOTES:")
            f.write("\n• Speak with high energy and enthusiasm")
            f.write("\n• Pause between sections for editing")
            f.write("\n• Emphasize money amounts and timeframes")
            f.write("\n• Show genuine excitement about results")
            f.write("\n• Include clear calls-to-action")
        
        return script_path

    def create_audio(self, script_path):
        """Step 2: Create audio from script"""
        audio_path = f"outputs/audio/{self.project_id}_audio.wav"
        
        # Read script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Clean script for TTS (remove formatting and notes)
        lines = script_content.split('\n')
        clean_lines = []
        for line in lines:
            if not line.startswith('🎬') and not line.startswith('🎯') and not line.startswith('📊') and not line.startswith('💰') and not line.startswith('🔔') and not line.startswith('•') and not line.startswith('=') and line.strip():
                clean_line = line.replace('[', '').replace(']', '').strip()
                if clean_line and not clean_line.startswith('PROJECT:') and not clean_line.startswith('TITLE:'):
                    clean_lines.append(clean_line)
        
        clean_script = ' '.join(clean_lines)
        
        # Try different TTS methods
        success = False
        
        # Method 1: macOS 'say' command
        if os.system("which say") == 0:
            try:
                temp_aiff = f"outputs/audio/{self.project_id}_temp.aiff"
                cmd = f'say "{clean_script}" -o "{temp_aiff}"'
                if os.system(cmd) == 0:
                    # Convert to WAV if ffmpeg available
                    if os.system("which ffmpeg") == 0:
                        convert_cmd = f'ffmpeg -i "{temp_aiff}" "{audio_path}" -y'
                        if os.system(convert_cmd) == 0:
                            os.remove(temp_aiff)
                            success = True
                    else:
                        # Rename aiff to wav (basic compatibility)
                        os.rename(temp_aiff, audio_path)
                        success = True
            except Exception as e:
                print(f"macOS TTS failed: {e}")
        
        # Method 2: Linux espeak
        if not success and os.system("which espeak") == 0:
            try:
                cmd = f'espeak "{clean_script}" -w "{audio_path}"'
                if os.system(cmd) == 0:
                    success = True
            except Exception as e:
                print(f"Linux TTS failed: {e}")
        
        # Method 3: Create manual recording guide
        if not success:
            audio_path = f"outputs/audio/{self.project_id}_recording_guide.txt"
            with open(audio_path, 'w') as f:
                f.write("🎙️ MANUAL RECORDING REQUIRED\n")
                f.write("="*50 + "\n\n")
                f.write("CLEAN SCRIPT FOR RECORDING:\n")
                f.write("-"*30 + "\n")
                f.write(clean_script)
                f.write("\n\n" + "-"*30)
                f.write("\n\n🎵 RECORDING INSTRUCTIONS:")
                f.write("\n• Use a quiet environment")
                f.write("\n• Speak clearly and with energy")
                f.write("\n• Record in sections for easier editing")
                f.write("\n• Save as WAV or high-quality MP3")
                f.write(f"\n• Name the file: {self.project_id}_audio.wav")
            print("⚠️  TTS not available - Manual recording guide created")
        
        return audio_path

    def create_thumbnail(self):
        """Step 3: Create thumbnail guide and prompt"""
        thumbnail_path = f"outputs/thumbnails/{self.project_id}_thumbnail_complete.txt"
        
        with open(thumbnail_path, 'w') as f:
            f.write(f"🎨 THUMBNAIL CREATION GUIDE\n")
            f.write(f"PROJECT: {self.project_id}\n")
            f.write(f"TITLE: {self.project_data['title']}\n")
            f.write("="*60 + "\n\n")
            
            f.write("🤖 AI PROMPT FOR DALL-E/MIDJOURNEY:\n")
            f.write("-"*40 + "\n")
            f.write(f"Create a YouTube thumbnail for '{self.project_data['title']}'. ")
            f.write("Show an excited person pointing at money symbols, dollar signs, and upward trending charts. ")
            f.write("Use bright colors (green, gold, red), large bold text overlay, high contrast for mobile viewing. ")
            f.write("Professional, clickbait style, 1280x720 resolution.\n\n")
            
            f.write("🎨 CANVA TEMPLATE INSTRUCTIONS:\n")
            f.write("-"*40 + "\n")
            f.write("1. Open Canva Pro → YouTube Thumbnail\n")
            f.write("2. Search 'Money YouTube Thumbnail' templates\n")
            f.write("3. Replace text with main hook from title\n")
            f.write("4. Add elements: 💰 $ 📈 ⬆️ 🔥\n")
            f.write("5. Use fonts: Impact, Bebas Neue, or Oswald\n")
            f.write("6. Colors: #00FF00 (green), #FFD700 (gold), #FF0000 (red)\n")
            f.write("7. Export as PNG, 1280x720\n\n")
            
            f.write("📱 MOBILE OPTIMIZATION:\n")
            f.write("-"*40 + "\n")
            f.write("• Text size: Minimum 60pt font\n")
            f.write("• High contrast colors only\n")
            f.write("• Test visibility on small screen\n")
            f.write("• Avoid cluttered designs\n")
            f.write("• Face should be clearly visible\n\n")
            
            f.write("🎯 PSYCHOLOGICAL TRIGGERS:\n")
            f.write("-"*40 + "\n")
            f.write("• Excited/surprised facial expression\n")
            f.write("• Pointing gesture toward money/results\n")
            f.write("• Money symbols prominently displayed\n")
            f.write("• Urgency indicators (arrows, highlights)\n")
            f.write("• Social proof elements if possible\n\n")
            
            f.write(f"💾 SAVE AS: {self.project_id}_thumbnail.png\n")
            f.write("📍 LOCATION: outputs/thumbnails/\n")
        
        return thumbnail_path

    def create_video(self, audio_path, thumbnail_path):
        """Step 4: Create video (multiple options)"""
        video_path = f"outputs/videos/{self.project_id}_video.mp4"
        
        # Check if we have actual audio file
        if audio_path.endswith('.wav') and os.path.exists(audio_path):
            # Try to create video with ffmpeg
            if os.system("which ffmpeg") == 0:
                # Create a simple colored background if no thumbnail image exists
                temp_image = f"outputs/thumbnails/{self.project_id}_temp_bg.png"
                
                # Create temporary background image
                create_bg_cmd = f'ffmpeg -f lavfi -i color=c=blue:size=1280x720:d=1 -frames:v 1 "{temp_image}" -y'
                os.system(create_bg_cmd)
                
                # Create video with audio and background
                video_cmd = f'ffmpeg -loop 1 -i "{temp_image}" -i "{audio_path}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "{video_path}" -y'
                
                if os.system(video_cmd) == 0:
                    os.remove(temp_image)  # Clean up
                    print("✅ Basic video created with audio")
                    return video_path
                else:
                    print("⚠️ Video creation failed, creating guide instead")
            
        # Create comprehensive video creation guide
        video_guide_path = f"outputs/videos/{self.project_id}_video_creation_guide.txt"
        
        with open(video_guide_path, 'w') as f:
            f.write(f"🎬 VIDEO CREATION GUIDE\n")
            f.write(f"PROJECT: {self.project_id}\n")
            f.write("="*60 + "\n\n")
            
            f.write("🎯 RECOMMENDED APPROACH: SCREEN RECORDING\n")
            f.write("-"*50 + "\n")
            f.write("This method works best for money-making content!\n\n")
            
            f.write("📱 TOOLS NEEDED:\n")
            f.write("• OBS Studio (Free) - obs-project.com\n")
            f.write("• OR Loom (Easy) - loom.com\n")
            f.write("• OR QuickTime (Mac) - Built-in\n\n")
            
            f.write("🖥️ WHAT TO RECORD:\n")
            f.write("1. Browser with relevant websites/dashboards\n")
            f.write("2. Spreadsheets showing calculations\n")
            f.write("3. Screenshots of earnings/results\n")
            f.write("4. Step-by-step process demonstrations\n")
            f.write("5. Tools and platforms mentioned in script\n\n")
            
            f.write("⚙️ RECORDING SETTINGS:\n")
            f.write("• Resolution: 1920x1080 (1080p)\n")
            f.write("• Frame Rate: 30fps\n")
            f.write("• Format: MP4\n")
            f.write("• Audio: Use separate audio file created earlier\n\n")
            
            f.write("🎨 VISUAL ELEMENTS TO INCLUDE:\n")
            f.write("• Money counters and calculators\n")
            f.write("• Charts showing growth/progress\n")
            f.write("• Before/after comparisons\n")
            f.write("• Step-by-step process flows\n")
            f.write("• Social proof (testimonials, results)\n\n")
            
            f.write("📊 SCREEN RECORDING TIMELINE:\n")
            f.write("0:00-0:15 - Hook: Show end results first\n")
            f.write("0:15-0:30 - Subscribe reminder with animation\n")
            f.write("0:30-2:00 - Problem demonstration\n")
            f.write("2:00-6:00 - Solution walkthrough\n")
            f.write("6:00-8:00 - Results and proof\n")
            f.write("8:00-9:00 - Call to action\n")
            f.write("9:00-10:00 - Subscribe + end screen\n\n")
            
            f.write("🎵 AUDIO SYNC:\n")
            f.write(f"• Import audio file: {audio_path}\n")
            f.write("• Sync with screen recording\n")
            f.write("• Add background music (low volume)\n")
            f.write("• Ensure clear voice throughout\n\n")
            
            f.write("💡 PRO TIPS:\n")
            f.write("• Record in segments for easier editing\n")
            f.write("• Use cursor highlighting/zoom effects\n")
            f.write("• Add text overlays for key points\n")
            f.write("• Include subscribe button animations\n")
            f.write("• Test audio levels before final export\n\n")
            
            f.write(f"💾 EXPORT SETTINGS:\n")
            f.write("• Format: MP4\n")
            f.write("• Quality: High (1080p)\n")
            f.write("• File name: {self.project_id}_final_video.mp4\n")
            f.write("• Location: outputs/videos/\n")
        
        return video_guide_path

    def create_upload_package(self):
        """Step 5: Create complete YouTube upload package"""
        package_path = f"outputs/upload_packages/{self.project_id}_upload_package.json"
        
        # Generate optimized title
        optimized_title = self.optimize_title(self.project_data['title'])
        
        # Generate description
        description = self.generate_description()
        
        # Generate tags
        tags = self.generate_tags()
        
        # Create complete package
        upload_package = {
            "project_id": self.project_id,
            "original_title": self.project_data['title'],
            "optimized_title": optimized_title,
            "description": description,
            "tags": tags,
            "category": "Education",
            "privacy": "public",
            "monetization": {
                "ads_enabled": True,
                "affiliate_links": True,
                "lead_magnets": True
            },
            "upload_timing": {
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "best_time": "2:00 PM EST",
                "timezone": "Eastern Standard Time"
            },
            "post_upload_checklist": [
                "Enable monetization immediately",
                "Add end screen with related videos",
                "Create community post announcement",
                "Share on social media",
                "Send email to subscriber list",
                "Monitor comments for first hour",
                "Pin top comment with call-to-action",
                "Add video to relevant playlists"
            ],
            "seo_optimization": {
                "primary_keyword": self.extract_primary_keyword(),
                "secondary_keywords": self.extract_secondary_keywords(),
                "hashtags": self.generate_hashtags()
            }
        }
        
        # Save package as JSON
        with open(package_path, 'w') as f:
            json.dump(upload_package, f, indent=2)
        
        # Also create human-readable version
        readable_path = f"outputs/upload_packages/{self.project_id}_upload_instructions.txt"
        with open(readable_path, 'w') as f:
            f.write(f"📤 YOUTUBE UPLOAD PACKAGE\n")
            f.write(f"PROJECT: {self.project_id}\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"🎯 OPTIMIZED TITLE:\n")
            f.write(f"{optimized_title}\n\n")
            
            f.write(f"📝 DESCRIPTION:\n")
            f.write("-"*30 + "\n")
            f.write(f"{description}\n\n")
            
            f.write(f"🏷️ TAGS:\n")
            f.write(", ".join(tags) + "\n\n")
            
            f.write(f"⚙️ UPLOAD SETTINGS:\n")
            f.write(f"• Category: Education\n")
            f.write(f"• Privacy: Public\n")
            f.write(f"• Language: English\n")
            f.write(f"• License: Standard YouTube License\n\n")
            
            f.write(f"⏰ OPTIMAL UPLOAD TIME:\n")
            f.write(f"• Best Days: Tuesday, Wednesday, Thursday\n")
            f.write(f"• Best Time: 2:00 PM EST\n")
            f.write(f"• Avoid: Monday mornings, Friday evenings\n\n")
            
            f.write(f"💰 MONETIZATION CHECKLIST:\n")
            for item in upload_package["post_upload_checklist"]:
                f.write(f"☐ {item}\n")
            
            f.write(f"\n🎯 SEO KEYWORDS:\n")
            f.write(f"Primary: {upload_package['seo_optimization']['primary_keyword']}\n")
            f.write(f"Secondary: {', '.join(upload_package['seo_optimization']['secondary_keywords'])}\n")
            f.write(f"Hashtags: {' '.join(upload_package['seo_optimization']['hashtags'])}\n")
        
        return package_path

    def optimize_title(self, title):
        """Optimize title for YouTube algorithm"""
        # Add urgency and proof elements
        if "How I Made" in title:
            return title + " (PROOF INSIDE)"
        elif "Secret" in title:
            return title + " - REVEALED 2024"
        elif "$" in title:
            return title + " (STEP BY STEP)"
        else:
            return title + " (WORKS IN 2024)"

    def generate_description(self):
        """Generate complete YouTube description"""
        return f"""🚀 {self.project_data['title']}

In this video, I reveal the EXACT method I used to generate ${self.project_data['revenue_potential']} online. This isn't theory - these are real results you can replicate starting today.

⏰ TIMESTAMPS:
00:00 - Introduction & Results Preview
00:30 - Why This Method Works
02:00 - Step-by-Step Breakdown
05:00 - Live Demonstration
08:00 - How You Can Start Today
09:00 - Subscribe for More!

💰 RESOURCES & TOOLS MENTIONED:
🔗 Complete Blueprint: [YOUR AFFILIATE LINK]
🔗 Recommended Tools: [YOUR AFFILIATE LINK]  
🔗 Free Training Course: [YOUR LEAD MAGNET]
🔗 Join Our Community: [YOUR DISCORD/FACEBOOK GROUP]

📊 CONNECT WITH ME:
• Instagram: @yourusername
• Twitter: @yourusername
• Email: contact@yourdomain.com
• Website: www.yourdomain.com

💡 RELATED VIDEOS:
• How I Made $10K in 30 Days: [LINK]
• Best Tools for Online Income: [LINK]
• Beginner's Guide to Making Money Online: [LINK]

⚠️ IMPORTANT DISCLAIMER:
Results shown are not typical. Individual results may vary based on effort, market conditions, and other factors. This video is for educational purposes only and should not be considered financial advice.

🎯 ABOUT THIS CHANNEL:
I share proven strategies for making money online, building passive income streams, and achieving financial freedom. Subscribe and hit the bell icon for weekly money-making content!

#MakeMoneyOnline #PassiveIncome #OnlineBusiness #SideHustle #FinancialFreedom #{self.project_data['niche']}

---
This video may contain affiliate links. I may earn a commission at no extra cost to you if you make a purchase through these links. Thank you for supporting the channel!"""

    def generate_tags(self):
        """Generate SEO-optimized tags"""
        base_tags = [
            "make money online",
            "passive income",
            "online business", 
            "side hustle",
            "financial freedom",
            "work from home",
            "internet marketing",
            f"{self.project_data['niche'].lower()} income"
        ]
        
        # Extract keywords from title
        title_words = self.project_data['title'].lower().replace('$', 'dollar').split()
        title_tags = [word for word in title_words if len(word) > 3 and word not in ['with', 'this', 'that', 'from', 'your']]
        
        # Combine and limit to 15 tags (YouTube limit)
        all_tags = base_tags + title_tags[:7]
        return all_tags[:15]

    def extract_primary_keyword(self):
        """Extract primary SEO keyword"""
        title_lower = self.project_data['title'].lower()
        if 'crypto' in title_lower:
            return 'make money with crypto'
        elif 'trading' in title_lower:
            return 'online trading income'
        elif 'business' in title_lower:
            return 'online business income'
        else:
            return 'make money online'

    def extract_secondary_keywords(self):
        """Extract secondary keywords"""
        return [
            'passive income streams',
            'financial freedom',
            f'{self.project_data["niche"].lower()} profits',
            'work from home income'
        ]

    def generate_hashtags(self):
        """Generate trending hashtags"""
        return [
            '#MakeMoneyOnline',
            '#PassiveIncome', 
            '#FinancialFreedom',
            f'#{self.project_data["niche"]}',
            '#SideHustle'
        ]

    def save_to_database(self):
        """Step 6: Save project to database"""
        conn = sqlite3.connect('youtube_projects.db')
        
        # Create table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT,
                niche TEXT,
                revenue_potential REAL,
                status TEXT,
                script_path TEXT,
                audio_path TEXT,
                thumbnail_path TEXT,
                video_path TEXT,
                upload_package_path TEXT,
                created_at TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Insert project
        conn.execute('''
            INSERT OR REPLACE INTO projects 
            (id, title, niche, revenue_potential, status, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.project_id,
            self.project_data['title'],
            self.project_data['niche'],
            self.project_data['revenue_potential'],
            'completed',
            datetime.now().isoformat(),
            json.dumps(self.project_data)
        ))
        
        conn.commit()
        conn.close()

    def print_completion_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📋 Project ID: {self.project_id}")
        print(f"📝 Title: {self.project_data['title']}")
        print(f"💰 Revenue Potential: ${self.project_data['revenue_potential']}")
        print(f"🎯 Niche: {self.project_data['niche']}")
        print("\n📁 FILES CREATED:")
        print(f"• Script: outputs/scripts/{self.project_id}_script.txt")
        print(f"• Audio: outputs/audio/{self.project_id}_audio.*")
        print(f"• Thumbnail Guide: outputs/thumbnails/{self.project_id}_thumbnail_complete.txt")
        print(f"• Video Guide: outputs/videos/{self.project_id}_video_creation_guide.txt")
        print(f"• Upload Package: outputs/upload_packages/{self.project_id}_upload_package.json")
        print("\n🚀 NEXT STEPS:")
        print("1. Create thumbnail using the AI prompt provided")
        print("2. Record screen following the video guide")
        print("3. Upload to YouTube using the upload package")
        print("4. Enable monetization immediately after upload")
        print("5. Promote on social media and to email list")
        print("\n💡 PRO TIP: Upload during optimal times (Tue-Thu, 2PM EST)")
        print("="*60)

def main():
    """Main function to run the complete pipeline"""
    print("🎬 COMPLETE YOUTUBE PRODUCTION PIPELINE")
    print("="*60)
    
    # Get user input
    print("\n📝 Enter video details:")
    title = input("Video Title: ").strip()
    if not title:
        title = "How I Made $5,000 in 30 Days with This Simple Method"
    
    niche = input("Niche (crypto/finance/business/tech): ").strip().lower()
    if not niche:
        niche = "finance"
    
    try:
        revenue_input = input("Revenue Potential ($): ").strip()
        revenue_potential = float(revenue_input) if revenue_input else 5000.0
    except ValueError:
        revenue_potential = 5000.0
    
    # Initialize and run pipeline
    pipeline = CompleteYouTubePipeline()
    result = pipeline.run_complete_pipeline(title, niche, revenue_potential)
    
    if result['success']:
        print(f"\n✅ Pipeline completed! Project ID: {result['project_id']}")
        
        # Show file locations
        print("\n📁 Generated Files:")
        for file_type, file_path in result['files'].items():
            print(f"• {file_type.title()}: {file_path}")
        
        # Ask if user wants to run another
        another = input("\nRun another pipeline? (y/n): ").strip().lower()
        if another == 'y':
            main()
    else:
        print(f"\n❌ Pipeline failed: {result['error']}")

if __name__ == "__main__":
    main()
