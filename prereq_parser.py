import re
import json

class PrerequisiteParser:
    """Parses and evaluates course prerequisites"""

    def __init__(self):
        # Course equivalents (Oxford campus variants)
        self.equivalents = {
            'CS_OX 170': 'CS 170',
            'CS_OX 171': 'CS 171',
            'CS_OX 224': 'CS 224',
            'CS_OX 253': 'CS 253',
            'MATH_OX 111': 'MATH 111',
            'MATH_OX 221': 'MATH 221',
        }

    def normalize_course(self, course):
        """Convert Oxford courses to main campus equivalents"""
        course = course.strip()
        return self.equivalents.get(course, course)

    def parse_prereqs(self, prereq_string):
        """
        Parse prerequisite string into structured format
        Returns: list of requirement groups (AND of ORs)
        """
        if not prereq_string or prereq_string == "None":
            return []
        
        # Remove common noise phrases
        prereq_string = prereq_string.lower()
        prereq_string = re.sub(r'or equivalent transfer credit as (a )?prerequisite\.?', '', prereq_string)
        prereq_string = re.sub(r'this course requires?', '', prereq_string)

        # Extract course codes (CS 123, MATH 221, etc.)
        # Pattern matches: DEPT NUMBERLETTER (e.g., CS 171, CS 171Z, MATH_OX 221)
        course_pattern = r'\b([A-Z]+_?[A-Z]*\s+\d+[A-Z]?)\b'

        # Split by "and" to get requirement groups
        and_groups = re.split(r'\s+and\s+', prereq_string)

        requirements = []

        for group in and_groups:
            # Find all courses in this group (these are OR'd together)
            courses = re.findall(course_pattern, group, re.IGNORECASE)

            if courses:
                # Normalize courses (remove duplicates after normalization)
                normalized = list(set([self.normalize_course(c.upper()) for c in courses]))
                requirements.append(normalized)
        
        return requirements

    def check_eligibility(self, completed_courses, prereq_string):
        """
        Check if student has completed prerequisites

        Args:
            completed_courses: list of course codes student has taken
            prereq_string: the prerequisite requirement string
        
        Returns:
            (eligible: bool, missing: list of requirement groups)
        """
        requirements = self.parse_prereqs(prereq_string)

        if not requirements:
            return True, []
        
        # Normalize completed courses
        completed_normalized = set([self.normalize_course(c.upper()) for c in completed_courses])

        missing = []

        # Check each AND group
        for req_group in requirements:
            # Student needs at least ONE course from this group (OR logic)
            has_any = any(course in completed_normalized for course in req_group)

            if not has_any:
                missing.append(req_group)
        
        eligible = len(missing) == 0
        return eligible, missing

    def explain_missing(self, missing_groups):
        """Generate human-readable explanation of missing prerequisites"""
        if not missing_groups:
            return "No missing prerequisites"
        
        explanations = []
        for group in missing_groups:
            if len(group) == 1:
                explanations.append(f"• {group[0]}")
            else:
                explanations.append(f"• One of: {' OR '.join(group)}")

        return "Missing prerequisites:\n" + "\n".join(explanations)


# Test the parser
if __name__ == "__main__":
    parser = PrerequisiteParser()

    print("="*60)
    print("TESTING PREREQUISITE PARSER")
    print("="*60)

    # Test case 1: CS 334 (Machine Learning)
    prereq_cs334 = "(CS224 or CS_OX 224) and (CS 253 or CS_OX 253) and (MATH 221 or MATH_OX 221 or MATH 275 or MATH 321) or equivalent transfer credit as prerequisite."

    print("\n1. Testing CS 334 prerequisites:")
    print(f"   Prereq string: {prereq_cs334}")

    parsed = parser.parse_prereqs(prereq_cs334)
    print(f"\n   Parsed requirements (AND groups):")
    for i, group in enumerate(parsed, 1):
        print(f"   {i}. {' OR '.join(group)}")

    # Test with student who has taken required courses
    completed = ['CS 170', 'CS 171', 'CS 224', 'CS 253', 'MATH 221']
    eligible, missing = parser.check_eligibility(completed, prereq_cs334)

    print(f"\n   Student completed: {', '.join(completed)}")
    print(f"   Eligible for CS 334? {eligible}")
    if not eligible:
        print(f"\n   {parser.explain_missing(missing)}")

    # Test with student missing courses
    print("\n" + "="*60)
    completed_partial = ['CS 170', 'CS 171', 'CS 224']
    eligible2, missing2 = parser.check_eligibility(completed_partial, prereq_cs334)

    print("2. Testing with partial completion:")
    print(f"   Student completed: {', '.join(completed_partial)}")
    print(f"   Eligible for CS 334? {eligible2}")
    if not eligible2:
        print(f"\n   {parser.explain_missing(missing2)}")

    print("\n" + "="*60)