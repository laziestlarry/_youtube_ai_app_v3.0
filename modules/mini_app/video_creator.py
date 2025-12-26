"""
Simple Video Creator for YouTube Content
"""
import os
import subprocess
from pathlib import Path

class SimpleVideoCreator:
    def __init__(self):
        self.output_dir = Path("outputs/videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_video_options(self, project_id: str):
        """Show video creation options"""
        print("🎬 VIDEO CREATION OPTIONS:")
        print("1. Static Thumbnail + Audio (Simplest)")
        print("2. Screen Recording + Audio (Recommended)")
        print("3. Stock Footage + Audio (Professional)")
        print("4. AI Avatar + Audio (Advanced)")
        
        choice = input("Choose option (1-4): ")
        
        if choice == "1":
            return self.static_video(project_id)
        elif choice == "2":
            return self.screen_recording_guide(project_id)
        elif choice == "3":
            return self.stock_footage_guide(project_id)
        else:
            return self.ai_avatar_guide(project_id)
    
    def static_video(self, project_id: str):
        """Create static thumbnail video"""
        thumbnail_path = f"outputs/thumbnails/{project_id}_thumbnail.jpg"
        audio_path = f"outputs/audio/{project_id}_audio.wav"
        output_path = f"outputs/videos/{project_id}_video.mp4"
        
        if not os.path.exists(thumbnail_path):
            print("❌ Create thumbnail first!")
            return None
        
        if not os.path.exists(audio_path):
            print("❌ Create audio first!")
            return None
        
        # Create video with ffmpeg
        cmd = f'''ffmpeg -loop 1 -i "{thumbnail_path}" -i "{audio_path}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "{output_path}" -y'''
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Video created: {output_path}")
            return output_path
        except subprocess.CalledProcessError:
            print("❌ Video creation failed. Install ffmpeg first.")
            return None
    
    def screen_recording_guide(self, project_id: str):
        """Create screen recording guide"""
        guide_path = f"outputs/videos/{project_id}_screen_recording_guide.txt"
        
        with open(guide_path, 'w') as f:
            f.write("🖥️ SCREEN RECORDING GUIDE\n")
            f.write("="*50 + "\n\n")
            f.write("RECOMMENDED TOOLS:\n")
            f.write("• OBS Studio (Free, Professional)\n")
            f.write("• Loom (Easy, Web-based)\n")
            f.write("• Camtasia (Paid, User-friendly)\n\n")
            f.write("CONTENT TO RECORD:\n")
            f.write("• Browser with relevant websites/tools\n")
            f.write("• Charts and graphs showing results\n")
            f.write("• Step-by-step process demonstrations\n")
            f.write("• Social proof (earnings screenshots)\n\n")
            f.write("RECORDING SETTINGS:\n")
            f.write("• Resolution: 1920x1080 (1080p)\n")
            f.write("• Frame Rate: 30fps\n")
            f.write("• Format: MP4\n")
            f.write("• Audio: Record separately for better quality\n")
        
        print(f"📄 Screen recording guide: {guide_path}")
        return guide_path

# Run video creator
if __name__ == "__main__":
    creator = SimpleVideoCreator()
    project_id = input("Enter project ID: ")
    creator.create_video_options(project_id)