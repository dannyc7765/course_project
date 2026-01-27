from flask import Flask, render_template, request, jsonify
from course_finder import CourseFinder

app = Flask(__name__)
finder = CourseFinder()

@app.route('/')
def index():
    # Main page
    return render_template('index.html')

@app.route('/api/find-courses', methods=['POST'])
def find_courses():
    # API endpoint to find eligible courses
    data = request.get_json()
    completed_courses = data.get('completed)courses', [])
    
    #Clean up the input
    completed_courses = [c.strip().upper() for c in completed_courses if c.strip()]

    # Find eligible courses
    results = finder.find_eligible_courses(completed_courses)

    # Group by level for easier display
    eligible_by_level = {'100': [], '200': [], '300': [], '400': []}

    for course in results['eligible']:
        level = course['code'].split()[1][0] + '00'
        if level in eligible_by_level:
            eligible_by_level[level].append(course)
    
    return jsonify({
        'success': True,
        'completed_count': len(completed_courses),
        'eligible_count': len(results['eligible']),
        'eligible_by_level': eligible_by_level
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)


