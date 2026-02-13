import unittest
import os
import shutil
import tempfile
from scripts import audit_skills

class TestAuditSkills(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        self.skills_dir = os.path.join(self.test_dir, 'skills')
        os.makedirs(self.skills_dir)
        
        # Override the SKILLS_DIR in the module (we'll need to make sure the script supports this)
        # For now, we will assume the script takes the directory as an argument or we patch it
        self.audit = audit_skills.SkillAuditor(self.skills_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_missing_skill_md(self):
        # Create a skill without SKILL.md
        os.makedirs(os.path.join(self.skills_dir, 'bad-skill'))
        
        report = self.audit.check_skill('bad-skill')
        self.assertFalse(report['valid'])
        self.assertTrue(any("Missing SKILL.md" in e for e in report['errors']))

    def test_invalid_frontmatter(self):
        # Create a skill with invalid frontmatter
        skill_path = os.path.join(self.skills_dir, 'invalid-frontmatter')
        os.makedirs(skill_path)
        with open(os.path.join(skill_path, 'SKILL.md'), 'w') as f:
            f.write("# Just markdown, no yaml")
            
        report = self.audit.check_skill('invalid-frontmatter')
        self.assertFalse(report['valid'])
        self.assertTrue(any("Invalid YAML frontmatter" in e for e in report['errors']))
    
    def test_valid_skill(self):
        # Create a valid skill
        skill_path = os.path.join(self.skills_dir, 'good-skill')
        os.makedirs(skill_path)
        with open(os.path.join(skill_path, 'SKILL.md'), 'w') as f:
            f.write("---\nname: good-skill\ndescription: A valid skill\n---\n# Instructions")
            
        report = self.audit.check_skill('good-skill')
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['errors']), 0)

    def test_invalid_directory_structure(self):
        # Create a skill with a loose file
        skill_path = os.path.join(self.skills_dir, 'loose-file-skill')
        os.makedirs(skill_path)
        with open(os.path.join(skill_path, 'SKILL.md'), 'w') as f:
            f.write("---\nname: loose-file-skill\ndescription: Skill with loose file\n---\n")
        
        # Create a loose file that is not SKILL.md
        with open(os.path.join(skill_path, 'random.txt'), 'w') as f:
            f.write("I shouldn't be here")
            
        report = self.audit.check_skill('loose-file-skill')
        self.assertFalse(report['valid'])
        self.assertTrue(any("Loose file found" in e for e in report['errors']))

    def test_non_kebab_case(self):
         # Create a skill with snake_case name
        skill_name = 'snake_case_skill'
        skill_path = os.path.join(self.skills_dir, skill_name)
        os.makedirs(skill_path)
        with open(os.path.join(skill_path, 'SKILL.md'), 'w') as f:
             f.write("---\nname: snake_case_skill\ndescription: Skill with bad name\n---\n")
        
        # We need to test the runner part or a separate name checker
        # Assuming check_skill also validates the folder name if passed or we check it separately
        # Let's verify directory naming compliance is part of the audit
        
        is_compliant = self.audit.check_naming_convention(skill_name)
        self.assertFalse(is_compliant)

if __name__ == '__main__':
    unittest.main()
