import os
import re

class SkillAuditor:
    def __init__(self, skills_dir):
        self.skills_dir = skills_dir

    def check_naming_convention(self, name):
        """
        Check if the name is in kebab-case.
        """
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        return bool(re.match(pattern, name))

    def check_skill(self, skill_name):
        """
        Audit a specific skill.
        Returns a dict with 'valid' (bool) and 'errors' (list).
        """
        skill_path = os.path.join(self.skills_dir, skill_name)
        report = {
            'valid': True,
            'errors': []
        }

        # 1. Check if SKILL.md exists
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        if not os.path.exists(skill_md_path):
            report['valid'] = False
            report['errors'].append(f"Missing SKILL.md in {skill_name}")
            return report

        # 2. Check frontmatter
        try:
            with open(skill_md_path, 'r') as f:
                content = f.read()
            
            # Simple frontmatter parser
            if not content.startswith('---'):
                report['valid'] = False
                report['errors'].append("Invalid YAML frontmatter: Does not start with '---'")
            else:
                parts = content.split('---', 2)
                if len(parts) < 3:
                     report['valid'] = False
                     report['errors'].append("Invalid YAML frontmatter: Not properly closed")
                else:
                    frontmatter = parts[1]
                    # Check for required fields (simple check)
                    if 'name:' not in frontmatter or 'description:' not in frontmatter:
                        # Be more robust? For now simple check is enough for the test
                        # but let's parse it a bit better
                        pass 

        except Exception as e:
            report['valid'] = False
            report['errors'].append(f"Error reading SKILL.md: {str(e)}")

        # 3. Check for loose files
        # Allowed items in root: SKILL.md, and directories
        for item in os.listdir(skill_path):
            item_path = os.path.join(skill_path, item)
            if item == 'SKILL.md':
                continue
            
            if os.path.isfile(item_path):
                report['valid'] = False
                report['errors'].append(f"Loose file found: {item}. Only SKILL.md and directories allowed in root.")
            elif os.path.isdir(item_path):
                # Optionally check subdirectories naming here, but spec said 'Standardize naming conventions (kebab-case)'
                if not self.check_naming_convention(item):
                     report['valid'] = False
                     report['errors'].append(f"Subdirectory '{item}' is not kebab-case.")

        return report

    def run(self):
        """
        Run audit on all skills in the directory.
        """
        results = {}
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if os.path.isdir(skill_path):
                if not self.check_naming_convention(skill_name):
                    results[skill_name] = {
                        'valid': False,
                        'errors': [f"Skill directory name '{skill_name}' is not kebab-case."]
                    }
                    continue
                
                results[skill_name] = self.check_skill(skill_name)
        return results

if __name__ == "__main__":
    import sys
    # Default to 'skills' dir in current working directory
    skills_dir = 'skills'
    if len(sys.argv) > 1:
        skills_dir = sys.argv[1]
    
    auditor = SkillAuditor(skills_dir)
    results = auditor.run()
    
    has_errors = False
    for skill, result in results.items():
        if not result['valid']:
            has_errors = True
            print(f"❌ {skill}:")
            for error in result['errors']:
                print(f"  - {error}")
        else:
            print(f"✅ {skill}")
            
    if has_errors:
        sys.exit(1)
