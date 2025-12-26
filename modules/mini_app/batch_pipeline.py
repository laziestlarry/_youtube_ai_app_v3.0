"""
Batch Pipeline - Create Multiple Videos at Once
"""
from complete_sequential_pipeline import CompleteYouTubePipeline
import json
import time

class BatchPipeline:
    def __init__(self):
        self.pipeline = CompleteYouTubePipeline()
        self.results = []
    
    def run_batch(self, video_ideas):
        """Run pipeline for multiple videos"""
        print(f"🚀 Starting batch pipeline for {len(video_ideas)} videos...")
        
        for i, idea in enumerate(video_ideas, 1):
            print(f"\n📹 Processing Video {i}/{len(video_ideas)}")
            print(f"Title: {idea['title']}")
            
            result = self.pipeline.run_complete_pipeline(
                idea['title'],
                idea['niche'], 
                idea['revenue_potential']
            )
            
            self.results.append(result)
            
            # Small delay between videos
            time.sleep(2)
        
        self.print_batch_summary()
        return self.results
    
    def print_batch_summary(self):
        """Print summary of batch processing"""
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING COMPLETE")
        print("="*60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Total Projects: {len(self.results)}")
        
        if successful > 0:
            print(f"\n🎯 SUCCESS PROJECTS:")
            for result in self.results:
                if result['success']:
                    print(f"• {result['project_id']}")

def main():
    """Run batch pipeline with predefined ideas"""
    
    # High-converting video ideas
    video_ideas = [
        {
            "title": "How I Made $10,000 in 30 Days with Crypto Trading",
            "niche": "crypto",
            "revenue_potential": 15000
        },
        {
            "title": "The Amazon FBA Secret That Made Me $25,000",
            "niche": "business", 
            "revenue_potential": 25000
        },
        {
            "title": "I Tried Dropshipping for 60 Days - Made $8,500",
            "niche": "business",
            "revenue_potential": 12000
        },
        {
            "title": "Why Everyone is Using AI to Make $5,000 Monthly",
            "niche": "tech",
            "revenue_potential": 8000
        },
        {
            "title": "The Passive Income Method That Changed My Life",
            "niche": "finance",
            "revenue_potential": 20000
        }
    ]
    
    batch = BatchPipeline()
    batch.run_batch(video_ideas)

if __name__ == "__main__":
    main()