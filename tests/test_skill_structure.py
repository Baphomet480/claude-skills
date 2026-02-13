import unittest
import os
import re

class TestSkillStructure(unittest.TestCase):
    def setUp(self):
        # We assume the test is run from the project root
        self.skills_dir = 'skills'

    def check_kebab_case(self, name):
        # Allow dots for extensions, but main part must be kebab
        # e.g. file-name.txt is valid
        # file_name.txt is invalid
        # file-name.tar.gz is valid
        if name.startswith('.'): # Ignore hidden files like .DS_Store
            return True
            
        # Split by dot to handle extensions
        parts = name.split('.')
        stem = parts[0]
        
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        return bool(re.match(pattern, stem))

    def test_cloudflare_pages_structure(self):
        skill_name = 'cloudflare-pages'
        skill_path = os.path.join(self.skills_dir, skill_name)
        
        if not os.path.exists(skill_path):
            self.skipTest(f"Skill {skill_name} not found")

        # Check all files in skill directory recursively
        for root, dirs, files in os.walk(skill_path):
            for filename in files:
                if filename == 'SKILL.md':
                    continue
                # Check if filename is kebab-case
                rel_path = os.path.relpath(os.path.join(root, filename), self.skills_dir)
                self.assertTrue(self.check_kebab_case(filename), f"File '{filename}' (in {rel_path}) is not kebab-case")
            
            for dirname in dirs:
                self.assertTrue(self.check_kebab_case(dirname), f"Directory '{dirname}' (in {root}) is not kebab-case")
