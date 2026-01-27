import requests
from bs4 import BeautifulSoup
import json
import re

def clean_text(text):
    """Remove extra whitespace and newlines"""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_cs_courses():
    url = "https://catalog.college.emory.edu/academics/departments/computer-science.html"
    
    print("Fetching course catalog...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    courses = []
    
    # Find all accordion sections (100-level, 200-level, etc.)
    accordions = soup.find_all('div', class_='accordion')
    print(f"Found {len(accordions)} course level sections")
    
    for accordion in accordions:
        # Find all course cards within this accordion
        cards = accordion.find_all('div', class_='card')
        
        for card in cards:
            try:
                # Get course title button
                button = card.find('button', class_='accordion__toggle')
                if not button:
                    continue
                    
                title = clean_text(button.get_text())
                
                # Extract course code and name
                match = re.match(r'(CS \d+[A-Z]*):?\s*(.+)', title)
                if not match:
                    continue
                    
                course_code = match.group(1)
                course_name = match.group(2)
                
                # Get course body (collapsed content)
                card_body = card.find('div', class_='card-body')
                if not card_body:
                    continue
                
                # Get course description (first paragraph)
                description_p = card_body.find('p', class_='card-text')
                description = clean_text(description_p.get_text()) if description_p else ""
                
                # Get course details from the dl tag
                details_dl = card_body.find('dl', class_='row')
                
                credit_hours = ""
                ger = ""
                requisites = ""
                cross_listed = ""
                
                if details_dl:
                    # Get all dt (term) and dd (definition) pairs
                    dts = details_dl.find_all('dt')
                    dds = details_dl.find_all('dd')
                    
                    for dt, dd in zip(dts, dds):
                        label = clean_text(dt.get_text())
                        value = clean_text(dd.get_text())
                        
                        if "Credit Hours" in label:
                            credit_hours = value
                        elif "GER" in label:
                            ger = value
                        elif "Requisites" in label:
                            requisites = value
                        elif "Cross-Listed" in label:
                            cross_listed = value
                
                course_data = {
                    "course_code": course_code,
                    "course_name": course_name,
                    "description": description,
                    "credit_hours": credit_hours,
                    "ger": ger,
                    "requisites": requisites,
                    "cross_listed": cross_listed
                }
                
                courses.append(course_data)
                print(f"✓ {course_code}: {course_name}")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
    
    return courses

def save_courses(courses, filename="cs_courses.json"):
    """Save courses to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(courses, indent=2, fp=f)
    print(f"\n{'='*50}")
    print(f"✓ Saved {len(courses)} courses to {filename}")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("EMORY CS COURSE SCRAPER")
    print("="*50 + "\n")
    
    courses = scrape_cs_courses()
    
    if courses:
        # Show sample of first course
        print("\n" + "="*50)
        print("SAMPLE COURSE (CS 334):")
        print("="*50)
        cs334 = next((c for c in courses if c['course_code'] == 'CS 334'), courses[0])
        for key, value in cs334.items():
            print(f"{key}: {value}")
        
        # Save to file
        save_courses(courses)
    else:
        print("\n✗ No courses found!")
