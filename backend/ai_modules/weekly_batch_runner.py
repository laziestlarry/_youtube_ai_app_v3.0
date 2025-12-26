# ai_modules/weekly_batch_runner.py

from ai_modules.task_orchestrator import VideoPipeline

weekly_plan = [
    {"day": "Mon", "title": "Top 5 AI Tools", "topic": "AI Tools", "voice_id": "default"},
    {"day": "Wed", "title": "GPT Productivity Case Study", "topic": "AI Productivity", "voice_id": "default"},
    {"day": "Fri", "title": "Weekend AI Poll", "topic": "AI Voice Styles", "voice_id": "default"}
]

def run_weekly_jobs():
    for job in weekly_plan:
        print(f"🚀 Generating: {job['title']} ({job['day']})")
        vp = VideoPipeline(topic=job["topic"], title=job["title"], voice_id=job["voice_id"])
        output = vp.full_run()
        print(f"✅ Completed: {output}\n")

if __name__ == "__main__":
    run_weekly_jobs()
