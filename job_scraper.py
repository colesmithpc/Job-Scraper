import requests
import json
from datetime import datetime
import time

# here you need to enter your specific app id and key
class TechJobScraper:
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        # TODO: move these to env variables or config file
        self.app_id = "YOUR_APP_ID"
        self.app_key = "YOUR_APP_KEY"
        self.country = "us"
        
    def search_jobs(self, keyword="software engineer", location="", results_per_page=50, max_pages=2):
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}...")
            
            url = f"{self.base_url}/{self.country}/search/{page}"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": keyword,
                "where": location,
                "results_per_page": results_per_page,
                "content-type": "application/json"
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                jobs = data.get("results", [])
                
                for job in jobs:
                    # grab the important stuff
                    job_data = {
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("display_name"),
                        "location": job.get("location", {}).get("display_name"),
                        "description": job.get("description", "")[:500], 
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "contract_type": job.get("contract_type"),
                        "created": job.get("created"),
                        "url": job.get("redirect_url"),
                        "category": job.get("category", {}).get("label")
                    }
                    all_jobs.append(job_data)
                
                print(f"Found {len(jobs)} jobs on page {page}")
                time.sleep(1) # don't hammer the api
                
            except requests.exceptions.RequestException as e:
                print(f"Error on page {page}: {e}")
                break
        
        return all_jobs
    
    def save_to_json(self, jobs, filename="tech_jobs.json"):
        output = {
            "scraped_at": datetime.now().isoformat(),
            "total_jobs": len(jobs),
            "jobs": jobs
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(jobs)} jobs to {filename}")


if __name__ == "__main__":
    scraper = TechJobScraper()
    
    # modify these to search for what you want
    keywords = ["software engineer", "python developer", "data scientist"]
    
    all_results = []
    for kw in keywords:
        print(f"\nSearching: {kw}")
        jobs = scraper.search_jobs(keyword=kw, results_per_page=50, max_pages=2)
        all_results.extend(jobs)
    
    scraper.save_to_json(all_results)
    print(f"Total: {len(all_results)} jobs")