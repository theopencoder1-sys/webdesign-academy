from .models import User
from apps.courses.models import Enrollment
from apps.projects.models import Project

def generate_cv(user):
    """Generate professional CV based on user's learning progress"""
    
    completed_courses = Enrollment.objects.filter(user=user, completed=True)
    projects = Project.objects.filter(user=user, status='published')
    
    skills = []
    for enrollment in completed_courses:
        skills.append(enrollment.course.title)
    
    cv = f"""
# {user.get_full_name() or user.username}
## Web Developer | Nairobi, Kenya

📧 {user.email} | 📱 {user.website or ''} | 💻 {user.github_username or ''}

---

### PROFESSIONAL SUMMARY
Aspiring web developer with hands-on experience building {projects.count()} projects and completing {completed_courses.count()} courses at WebDesign Academy. Proficient in modern web technologies including HTML5, CSS3, JavaScript, and responsive design.

### TECHNICAL SKILLS
"""
    
    for skill in skills:
        cv += f"- ✅ {skill}\n"
    
    cv += "\n### PROJECTS\n"
    for project in projects:
        cv += f"""
**{project.title}**
{project.description[:150]}
🔗 {project.live_url or project.github_url or 'View in portfolio'}
"""
    
    cv += f"""
### EDUCATION
**WebDesign Academy** — {completed_courses.count()} Courses Completed
Kenya 🇰🇪

### CERTIFICATIONS
"""
    for enrollment in completed_courses:
        cv += f"- {enrollment.course.title}\n"
    
    cv += """
### CONTACT
📧 """ + user.email + """
📍 Nairobi, Kenya
🌐 WebDesign Academy Graduate
"""
    
    return cv
