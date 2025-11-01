import os
import re
import pdfplumber
from typing import Dict, List


class CVParser:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'node.js',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'git', 'ci/cd', 'agile', 'scrum', 'machine learning', 'data analysis',
            'project management', 'communication', 'leadership', 'problem solving'
        ]

        self.certification_keywords = [
            'certified', 'certificate', 'certification', 'pmp', 'csm', 'aws certified',
            'azure certified', 'google cloud certified', 'oracle certified', 'microsoft certified'
        ]

    def parse(self, filepath: str) -> Dict:
        try:
            # Try with pdfplumber first (better for text extraction)
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            text = ""

        # Extract information
        name = self.extract_name(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        education = self.extract_education(text)
        certifications = self.extract_certifications(text)
        interests = self.extract_interests(text)

        return {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'experience': experience,
            'education': education,
            'certifications': certifications,
            'interests': interests,
            'text': text
        }

    def extract_name(self, text: str) -> str:
        # Simple name extraction - look for capitalized words at the beginning
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            words = line.strip().split()
            if len(words) >= 2 and all(word[0].isupper() for word in words if word):
                return ' '.join(words[:2])  # Return first two words as name
        return "Unknown"

    def extract_email(self, text: str) -> str:
        # Extract email using regex
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else "unknown@example.com"

    def extract_phone(self, text: str) -> str:
        # Extract phone number using regex
        pattern = r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
        match = re.search(pattern, text)
        return match.group(0) if match else "Unknown"

    def extract_skills(self, text: str) -> List[str]:
        # Extract skills by looking for keywords
        text_lower = text.lower()
        found_skills = []

        for skill in self.skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)

        return found_skills

    def extract_experience(self, text: str) -> str:
        # Extract experience section
        lines = text.split('\n')
        experience_lines = []
        in_experience_section = False

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
                in_experience_section = True
                continue
            elif in_experience_section and any(
                    keyword in line_lower for keyword in ['education', 'skills', 'certifications']):
                break
            elif in_experience_section and line.strip():
                experience_lines.append(line.strip())

        return '\n'.join(experience_lines) if experience_lines else "No experience information found"

    def extract_education(self, text: str) -> str:
        # Extract education section
        lines = text.split('\n')
        education_lines = []
        in_education_section = False

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['education', 'academic', 'university', 'college']):
                in_education_section = True
                continue
            elif in_education_section and any(
                    keyword in line_lower for keyword in ['experience', 'skills', 'certifications']):
                break
            elif in_education_section and line.strip():
                education_lines.append(line.strip())

        return '\n'.join(education_lines) if education_lines else "No education information found"

    def extract_certifications(self, text: str) -> List[str]:
        # Extract certifications by looking for keywords
        text_lower = text.lower()
        found_certifications = []

        # Simple approach: look for lines containing certification keywords
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in self.certification_keywords):
                found_certifications.append(line.strip())

        return found_certifications

    def extract_interests(self, text: str) -> List[str]:
        # Extract interests section
        lines = text.split('\n')
        interests_lines = []
        in_interests_section = False

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['interests', 'hobbies', 'activities']):
                in_interests_section = True
                continue
            elif in_interests_section and any(
                    keyword in line_lower for keyword in ['experience', 'skills', 'education', 'certifications']):
                break
            elif in_interests_section and line.strip():
                interests_lines.append(line.strip())

        return interests_lines if interests_lines else []