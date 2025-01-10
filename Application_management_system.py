import json
import os
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, filename='Project/applications.json'):
        self.filename = filename
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            self.write({})
            
    def read(self):
        try:
            with open(self.filename, 'r') as openfile:
                return json.load(openfile)
        except json.JSONDecodeError:
            self.write({})
            return {}
            
    def write(self, data):
        def convert_sets(obj):
            if isinstance(obj, dict):
                return {key: convert_sets(value) for key, value in obj.items()}
            elif isinstance(obj, set):
                return list(obj)
            return obj
        serializable_data = convert_sets(data)
        with open(self.filename, 'w') as openfile:
            json.dump(serializable_data, openfile, indent=4)
        return data
        
    def append_data(self, new_data):
        current_data = self.read()
        current_data.update(new_data)
        return self.write(current_data)
        
    def clean_data_file(self):
        with open(self.filename, 'w') as openfile:
            json.dump({}, openfile, indent=4)

class Application:
    def __init__(self, name: str, job_id: str, resume_link: str, skills: List[str], experience: int):
        self.name = name
        self.job_id = job_id
        self.resume_link = resume_link
        self.status = "submitted"
        self.timestamp = str(datetime.now())
        self.skills = skills
        self.experience = experience

    # to get the data in the json formate
    def to_dict(self):
        return {
            "name": self.name,
            "job_id": self.job_id,
            "resume_link": self.resume_link,
            "status": self.status,
            "timestamp": self.timestamp,
            "skills": self.skills,
            "experience": self.experience
        }
        
    @classmethod
    def from_dict(cls, data):
        app = cls(
            data["name"],
            data["job_id"],
            data["resume_link"],
            data["skills"],
            data["experience"]
        )
        app.status = data["status"]
        app.timestamp = data["timestamp"]
        return app

class ApplicationStorage:
    def __init__(self):
        self.db = Database()
        
    def add(self, application: Application) -> str:
        data = self.db.read()
        app_id = f"APP{len(data) + 1}"
        data[app_id] = application.to_dict()
        self.db.write(data)
        return app_id
        
    def get(self, app_id: str) -> Optional[Application]:
        data = self.db.read()
        if app_id in data:
            return Application.from_dict(data[app_id])
        return None
        
    def update_status(self, app_id: str, status: str):
        data = self.db.read()
        if app_id in data:
            data[app_id]["status"] = status
            self.db.write(data)
            
    def get_all(self) -> Dict[str, Application]:
        data = self.db.read()
        return {
            app_id: Application.from_dict(app_data)
            for app_id, app_data in data.items()
        }

class ReviewQueue:
    def __init__(self):
        self.db = Database('Project/review_queue.json')
        
    def add(self, app_id: str):
        data = self.db.read()
        queue = data.get("queue", [])
        queue.append(app_id)
        self.db.write({"queue": queue})
        
    def get_next(self) -> Optional[str]:
        data = self.db.read()
        queue = data.get("queue", [])
        if queue:
            app_id = queue.pop(0)
            self.db.write({"queue": queue})
            return app_id
        return None

class DecisionStack:
    def __init__(self):
        self.db = Database('Project/decisions.json')
        
    def add_decision(self, app_id: str, decision: str):
        data = self.db.read()
        decisions = data.get("decisions", [])
        decisions.append({
            "app_id": app_id,
            "decision": decision,
            "timestamp": str(datetime.now())
        })
        self.db.write({"decisions": decisions})

class ApplicationManagementSystem:
    def __init__(self):
        self.storage = ApplicationStorage()
        self.review_queue = ReviewQueue()
        self.decision_stack = DecisionStack()
        
    def submit_application(self, name: str, job_id: str, resume_link: str,
                         skills: List[str], experience: int) -> str:
        application = Application(name, job_id, resume_link, skills, experience)
        app_id = self.storage.add(application)
        self.review_queue.add(app_id)
        return app_id
        
    def process_next_application(self) -> Optional[str]:
        app_id = self.review_queue.get_next()
        if app_id:
            self.storage.update_status(app_id, "under_review")
        return app_id
        
    def make_decision(self, app_id: str, decision: str):
        self.storage.update_status(app_id, decision)
        self.decision_stack.add_decision(app_id, decision)
        
    def search_applications(self, criteria: str, value: str) -> List[str]:
        apps = self.storage.get_all()
        results = []
        for app_id, app in apps.items():
            if criteria == "name" and app.name.lower() == value.lower():
                results.append(app_id)
            elif criteria == "job_id" and app.job_id == value:
                results.append(app_id)
            elif criteria == "status" and app.status == value:
                results.append(app_id)
        return results
        
    def filter_applications(self, min_experience: int,
                          required_skills: List[str]) -> List[str]:
        apps = self.storage.get_all()
        return [
            app_id for app_id, app in apps.items()
            if app.experience >= min_experience
            and all(skill in app.skills for skill in required_skills)
        ]
        
    def generate_report(self) -> Dict:
        apps = self.storage.get_all()
        total = len(apps)
        by_position = {}
        status_counts = {
            "submitted": 0,
            "under_review": 0,
            "shortlisted": 0,
            "rejected": 0
        }
        
        applications = self.storage.get_all()
        
        for app in applications.values():
            if app.job_id not in by_position:
                by_position[app.job_id] = 0
            by_position[app.job_id] += 1
            
            current_status = app.status.lower()  
            if current_status in status_counts:
                status_counts[current_status] += 1
            
        
        queue_data = self.review_queue.db.read()
        current_queue = queue_data.get("queue", [])                
        status_counts["under_review"] = len(current_queue)
            
        return {
            "total_applications": total,
            "applications_by_position": by_position,
            "status_summary": status_counts
        }

def display_menu():
    print("\n=== Application Management System ===")
    print("1. Submit New Application")
    print("2. Process Next Application")
    print("3. View Application Queue")
    print("4. Search Applications")
    print("5. Filter Applications")
    print("6. Generate Report")
    print("7. Exit")
    return input("Select an option (1-7): ")

def get_application_details():
    print("\n=== Submit New Application ===")
    name = input("Enter applicant name: ")
    job_id = input("Enter job ID: ")
    resume_link = input("Enter resume link: ")
    skills = input("Enter skills (comma-separated): ").split(",")
    skills = [skill.strip() for skill in skills]
    
    while True:
        try:
            experience = int(input("Enter years of experience: "))
            break
        except ValueError:
            print("Please enter a valid number")
    
    return name, job_id, resume_link, skills, experience

def search_menu(ams):
    print("\n=== Search Applications ===")
    print("1. Search by Name")
    print("2. Search by Job ID")
    print("3. Search by Status")
    choice = input("Select search criteria (1-3): ")
    
    if choice == "1":
        value = input("Enter name to search: ")
        results = ams.search_applications("name", value)
    elif choice == "2":
        value = input("Enter job ID to search: ")
        results = ams.search_applications("job_id", value)
    elif choice == "3":
        value = input("Enter status to search (submitted/under_review/shortlisted/rejected): ")
        results = ams.search_applications("status", value)
    else:
        print("Invalid choice")
        return
    
    display_search_results(ams, results)

def filter_menu(ams):
    print("\n=== Filter Applications ===")
    while True:
        try:
            min_experience = int(input("Enter minimum years of experience: "))
            break
        except ValueError:
            print("Please enter a valid number")
    
    required_skills = input("Enter required skills (comma-separated): ").split(",")
    required_skills = [skill.strip() for skill in required_skills]
    
    results = ams.filter_applications(min_experience, required_skills)
    display_search_results(ams, results)

def display_search_results(ams, results):
    if not results:
        print("\nNo applications found.")
        return
        
    print(f"\nFound {len(results)} application(s):")
    for app_id in results:
        app = ams.storage.get(app_id)
        print(f"\nApplication ID: {app_id}")
        print(f"Name: {app.name}")
        print(f"Job ID: {app.job_id}")
        print(f"Status: {app.status}")
        print(f"Skills: {', '.join(app.skills)}")
        print(f"Experience: {app.experience} years")

def display_report(report):
    print("\n=== Application Report ===")
    print(f"Total Applications: {report['total_applications']}")
    
    print("\nApplications by Position:")
    for position, count in report['applications_by_position'].items():
        print(f"{position}: {count}")
    
    print("\nStatus Summary:")
    for status, count in report['status_summary'].items():
        print(f"{status}: {count}")

def main():
    ams = ApplicationManagementSystem()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            name, job_id, resume_link, skills, experience = get_application_details()
            app_id = ams.submit_application(name, job_id, resume_link, skills, experience)
            print(f"\nApplication submitted successfully! Application ID: {app_id}")
            
        elif choice == "2":
            app_id = ams.process_next_application()
            if app_id:
                app = ams.storage.get(app_id)
                print(f"\nProcessing application ID: {app_id}")
                print(f"Applicant: {app.name}")
                print(f"Job ID: {app.job_id}")
                
                decision = input("Enter decision (shortlisted/rejected): ").lower()
                while decision not in ["shortlisted", "rejected"]:
                    print("Invalid decision. Please enter 'shortlisted' or 'rejected'")
                    decision = input("Enter decision (shortlisted/rejected): ").lower()
                
                ams.make_decision(app_id, decision)
                print(f"Decision recorded: {decision}")
            else:
                print("\nNo applications in the queue.")
                
        elif choice == "3":
            data = ams.review_queue.db.read()
            queue = data.get("queue", [])
            if queue:
                print("\nCurrent Application Queue:")
                for i, app_id in enumerate(queue, 1):
                    app = ams.storage.get(app_id)
                    print(f"{i}. Application ID: {app_id} - {app.name} (Job ID: {app.job_id})")
            else:
                print("\nQueue is empty.")
                
        elif choice == "4":
            search_menu(ams)
            
        elif choice == "5":
            filter_menu(ams)
            
        elif choice == "6":
            report = ams.generate_report()
            display_report(report)
            
        elif choice == "7":
            print("\nThank you for using the Application Management System!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()


