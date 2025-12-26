"""
Project Manager - View, Edit, and Manage Created Projects
"""
import sqlite3
import json
import os
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.db_path = 'youtube_projects.db'
    
    def list_projects(self):
        """List all projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT id, title, niche, revenue_potential, status, created_at
            FROM projects 
            ORDER BY created_at DESC
        ''')
        
        projects = cursor.fetchall()
        conn.close()
        
        if not projects:
            print("📭 No projects found")
            return
        
        print("\n📋 YOUR YOUTUBE PROJECTS")
        print("="*80)
        print(f"{'ID':<10} {'Title':<40} {'Niche':<10} {'Revenue':<10} {'Status':<10}")
        print("-"*80)
        
        for project in projects:
            print(f"{project[0]:<10} {project[1][:38]:<40} {project[2]:<10} ${project[3]:<9} {project[4]:<10}")
    
    def view_project(self, project_id):
        """View detailed project information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = cursor.fetchone()
        conn.close()
        
        if not project:
            print(f"❌ Project {project_id} not found")
            return
        
        print(f"\n📋 PROJECT DETAILS: {project_id}")
        print("="*60)
        print(f"Title: {project[1]}")
        print(f"Niche: {project[2]}")
        print(f"Revenue Potential: ${project[3]}")
        print(f"Status: {project[4]}")
        print(f"Created: {project[9]}")
        
        # Check which files exist
        files = {
            'Script': f"outputs/scripts/{project_id}_script.txt",
            'Audio': f"outputs/audio/{project_id}_audio.wav",
            'Thumbnail': f"outputs/thumbnails/{project_id}_thumbnail_complete.txt",
            'Video': f"outputs/videos/{project_id}_video_creation_guide.txt",
            'Upload Package': f"outputs/upload_packages/{project_id}_upload_package.json"
        }
        
        print(f"\n📁 FILES STATUS:")
        for file_type, file_path in files.items():
            status = "✅" if os.path.exists(file_path) else "❌"
            print(f"{status} {file_type}: {file_path}")
    
    def delete_project(self, project_id):
        """Delete a project and its files"""
        confirm = input(f"⚠️  Delete project {project_id}? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Deletion cancelled")
            return
        
        # Delete from database
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()
        
        # Delete files
        file_patterns = [
            f"outputs/scripts/{project_id}_*",
            f"outputs/audio/{project_id}_*",
            f"outputs/thumbnails/{project_id}_*",
            f"outputs/videos/{project_id}_*",
            f"outputs/upload_packages/{project_id}_*"
        ]
        
        import glob
        for pattern in file_patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"🗑️  Deleted: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not delete {file_path}: {e}")
        
        print(f"✅ Project {project_id} deleted successfully")
    
    def export_project(self, project_id):
        """Export project as ZIP file"""
        import zipfile
        
        export_path = f"exports/{project_id}_export.zip"
        os.makedirs("exports", exist_ok=True)
        
        with zipfile.ZipFile(export_path, 'w') as zipf:
            # Add all project files
            file_patterns = [
                f"outputs/scripts/{project_id}_*",
                f"outputs/audio/{project_id}_*", 
                f"outputs/thumbnails/{project_id}_*",
                f"outputs/videos/{project_id}_*",
                f"outputs/upload_packages/{project_id}_*"
            ]
            
            import glob
            files_added = 0
            for pattern in file_patterns:
                for file_path in glob.glob(pattern):
                    zipf.write(file_path)
                    files_added += 1
            
            if files_added > 0:
                print(f"📦 Exported {files_added} files to: {export_path}")
            else:
                print(f"⚠️  No files found for project {project_id}")

def main():
    """Main project manager interface"""
    manager = ProjectManager()
    
    while True:
        print("\n🎬 PROJECT MANAGER")
        print("="*40)
        print("1. List all projects")
        print("2. View project details")
        print("3. Delete project")
        print("4. Export project")
        print("5. Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == '1':
            manager.list_projects()
        
        elif choice == '2':
            project_id = input("Enter project ID: ").strip()
            manager.view_project(project_id)
        
        elif choice == '3':
            project_id = input("Enter project ID to delete: ").strip()
            manager.delete_project(project_id)
        
        elif choice == '4':
            project_id = input("Enter project ID to export: ").strip()
            manager.export_project(project_id)
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()