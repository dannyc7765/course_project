import json
from prereq_parser import PrerequisiteParser

class CourseFinder:
    """Find courses a student is eligible to take"""
    
    def __init__(self, courses_file="cs_courses.json"):
        # Load course data
        with open(courses_file, 'r') as f:
            self.courses = json.load(f)
        
        self.parser = PrerequisiteParser()
    
    def find_eligible_courses(self, completed_courses):
        """
        Find all courses the student can take
        
        Args:
            completed_courses: list of course codes student has completed
            
        Returns:
            dict with 'eligible' and 'ineligible' lists
        """
        eligible = []
        ineligible = []
        
        for course in self.courses:
            course_code = course['course_code']
            course_name = course['course_name']
            prereqs = course['requisites']
            
            # Skip if already completed
            if course_code in completed_courses:
                continue
            
            # Check eligibility
            can_take, missing = self.parser.check_eligibility(completed_courses, prereqs)
            
            if can_take:
                eligible.append({
                    'code': course_code,
                    'name': course_name,
                    'description': course['description'][:100] + "..." if len(course['description']) > 100 else course['description']
                })
            else:
                ineligible.append({
                    'code': course_code,
                    'name': course_name,
                    'missing': missing
                })
        
        return {
            'eligible': eligible,
            'ineligible': ineligible
        }
    
    def display_results(self, results):
        """Pretty print the results"""
        eligible = results['eligible']
        
        print("\n" + "="*70)
        print(f"✓ YOU CAN TAKE {len(eligible)} COURSES:")
        print("="*70)
        
        # Group by level
        levels = {'100': [], '200': [], '300': [], '400': []}
        
        for course in eligible:
            level = course['code'].split()[1][0] + '00'
            if level in levels:
                levels[level].append(course)
        
        for level in ['100', '200', '300', '400']:
            if levels[level]:
                print(f"\n{level}-Level Courses:")
                print("-" * 70)
                for course in sorted(levels[level], key=lambda x: x['code']):
                    print(f"  {course['code']}: {course['name']}")
                    print(f"     {course['description']}")
                    print()


def interactive_mode():
    """Interactive command-line interface"""
    finder = CourseFinder()
    
    print("\n" + "="*70)
    print("EMORY CS COURSE ELIGIBILITY CHECKER")
    print("="*70)
    print("\nEnter the CS and Math courses you have completed.")
    print("Format: CS 170, CS 171, MATH 221 (comma-separated)")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Completed courses: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter at least one course.\n")
            continue
        
        # Parse input
        completed = [c.strip().upper() for c in user_input.split(',')]
        
        print(f"\nSearching for courses you can take...")
        results = finder.find_eligible_courses(completed)
        finder.display_results(results)
        
        print("\n" + "="*70)
        print()


if __name__ == "__main__":
    # Example usage
    finder = CourseFinder()
    
    # Test with a typical sophomore
    print("\nEXAMPLE: Sophomore who completed intro courses")
    completed_courses = ['CS 170', 'CS 171', 'CS 224', 'MATH 221']
    
    results = finder.find_eligible_courses(completed_courses)
    finder.display_results(results)
    
    print("\n" + "="*70)
    print("\nWant to try with your own courses? Run interactive mode!")
    print("="*70)
    
    response = input("\nStart interactive mode? (y/n): ").strip().lower()
    if response == 'y':
        interactive_mode()