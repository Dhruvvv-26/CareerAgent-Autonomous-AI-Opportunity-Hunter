
import logging
from agents.search_agent import _scrape_unstop

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_unstop():
    keywords = ["software engineer", "intern", "python"]
    print(f"Testing Unstop scraping with keywords: {keywords}")
    
    results = _scrape_unstop(keywords)
    
    print(f"\nFound {len(results)} total results from Unstop (Jobs + Internships).")
    
    if results:
        print("\nSample results:")
        for i, res in enumerate(results[:5]):
            print(f"{i+1}. {res['role']} at {res['company']}")
            print(f"   Location: {res['location']}")
            print(f"   Stipend: {res['stipend']}")
            print(f"   Link: {res['link']}")
            print(f"   Deadline: {res['deadline']}")
            print("-" * 30)
    else:
        print("No results found. Check if the API structure changed or if keywords are too specific.")

if __name__ == "__main__":
    test_unstop()
