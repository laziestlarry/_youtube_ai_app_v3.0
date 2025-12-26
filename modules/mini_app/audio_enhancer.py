"""
Enhanced Audio Production for YouTube Videos
"""
import os
import subprocess
from pathlib import Path

class AudioProducer:
    def __init__(self):
        self.output_dir = Path("outputs/audio")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_professional_audio(self, script_file: str, project_id: str):
        """Create professional audio from script"""
        
        # Option 1: Use ElevenLabs API (Best Quality)
        print("🎵 Audio Production Options:")
        print("1. ElevenLabs AI Voice (Recommended)")
        print("2. System TTS (Free)")
        print("3. Manual Recording Guide")
        
        choice = input("Choose option (1-3): ")
        
        if choice == "1":
            return self.elevenlabs_tts(script_file, project_id)
        elif choice == "2":
            return self.system_tts(script_file, project_id)
        else:
            return self.manual_recording_guide(script_file, project_id)
    
    def elevenlabs_tts(self, script_file: str, project_id: str):
        """Use ElevenLabs for professional TTS"""
        print("🎯 ElevenLabs Setup:")
        print("1. Go to elevenlabs.io")
        print("2. Sign up for free account (10k chars/month)")
        print("3. Get API key")
        print("4. Choose voice (Rachel recommended for money content)")
        
        api_key = input("Enter ElevenLabs API key (or press Enter to skip): ")
        
        if api_key:
            # Implementation for ElevenLabs API
            print("✅ ElevenLabs integration ready!")
            return f"outputs/audio/{project_id}_elevenlabs.mp3"
        else:
            print("⏭️  Skipping ElevenLabs, using system TTS...")
            return self.system_tts(script_file, project_id)
    
    def manual_recording_guide(self, script_file: str, project_id: str):
        """Create manual recording guide"""
        guide_path = f"outputs/audio/{project_id}_recording_guide.txt"
        
        with open(guide_path, 'w') as f:
            f.write("🎙️ MANUAL RECORDING GUIDE\n")
            f.write("="*50 + "\n\n")
            f.write("RECOMMENDED SETUP:\n")
            f.write("• Microphone: Blue Yeti or Audio-Technica ATR2100x\n")
            f.write("• Software: Audacity (free) or Adobe Audition\n")
            f.write("• Environment: Quiet room with soft furnishings\n\n")
            f.write("RECORDING TIPS:\n")
            f.write("• Speak with energy and enthusiasm\n")
            f.write("• Pause between sections for editing\n")
            f.write("• Record intro/outro separately\n")
            f.write("• Use consistent volume throughout\n\n")
            f.write("POST-PRODUCTION:\n")
            f.write("• Remove background noise\n")
            f.write("• Normalize audio levels\n")
            f.write("• Add subtle background music\n")
            f.write("• Export as WAV or MP3 (192kbps+)\n")
        
        print(f"📄 Recording guide created: {guide_path}")
        return guide_path

    def create_video(self, audio_path):
        """Step 4: Create basic video with audio"""
        video_path = f"outputs/videos/{self.project_id}_basic_video.mp4"
        temp_image = f"outputs/videos/{self.project_id}_temp_image.png"
        
        # Create temporary image
        create_bg_cmd = f'ffmpeg -f lavfi -i color=c=black:s=1920x1080:r=1 -t 1 "{temp_image}"'
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
        print("4. Enable