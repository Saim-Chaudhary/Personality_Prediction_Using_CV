import json
import math
from typing import List, Tuple, Dict
from models import candidate, job


class RankingSystem:
    def __init__(self):
        self.skill_weight = 0.3
        self.experience_weight = 0.2
        self.education_weight = 0.1
        self.certification_weight = 0.1
        self.personality_weight = 0.3

    def rank_candidates(self, candidates: List[candidate.Candidate], job_profile: job.Job) -> List[
        Tuple[candidate.Candidate, float]]:
        """
        Rank candidates based on their match with the job requirements.
        Returns a list of (candidate, score) tuples, sorted by score in descending order.
        """
        ranked_candidates = []

        for candidate_obj in candidates:
            score = self._calculate_candidate_score(candidate_obj, job_profile)
            ranked_candidates.append((candidate_obj, score))

        # Sort by score in descending order
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)

        return ranked_candidates

    def _calculate_candidate_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate a score for a candidate based on a job profile."""
        skill_score = self._calculate_skill_score(candidate_obj, job_profile)
        experience_score = self._calculate_experience_score(candidate_obj, job_profile)
        education_score = self._calculate_education_score(candidate_obj, job_profile)
        certification_score = self._calculate_certification_score(candidate_obj, job_profile)
        personality_score = self._calculate_personality_score(candidate_obj, job_profile)

        total_score = (
                skill_score * self.skill_weight +
                experience_score * self.experience_weight +
                education_score * self.education_weight +
                certification_score * self.certification_weight +
                personality_score * self.personality_weight
        )

        return total_score

    def _calculate_skill_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate skill match score."""
        if not job_profile.required_skills or not candidate_obj.skills:
            return 0.5  # Neutral score if no data

        required_skills = [skill.strip().lower() for skill in job_profile.required_skills.split(',')]
        candidate_skills = [skill.strip().lower() for skill in candidate_obj.skills.split(',')]

        if not required_skills:
            return 0.5

        match_count = sum(1 for skill in required_skills if skill in candidate_skills)
        return match_count / len(required_skills)

    def _calculate_experience_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate experience match score."""
        # This is a simplified version. In a real system, you'd parse years of experience.
        if not job_profile.required_experience or not candidate_obj.experience:
            return 0.5

        # Simple keyword matching for experience
        required_keywords = job_profile.required_experience.lower().split()
        candidate_experience_text = candidate_obj.experience.lower()

        match_count = sum(1 for keyword in required_keywords if keyword in candidate_experience_text)
        return match_count / len(required_keywords) if required_keywords else 0.5

    def _calculate_education_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate education match score."""
        if not job_profile.required_education or not candidate_obj.education:
            return 0.5

        required_keywords = job_profile.required_education.lower().split()
        candidate_education_text = candidate_obj.education.lower()

        match_count = sum(1 for keyword in required_keywords if keyword in candidate_education_text)
        return match_count / len(required_keywords) if required_keywords else 0.5

    def _calculate_certification_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate certification match score."""
        if not job_profile.required_certifications or not candidate_obj.certifications:
            return 0.5

        required_certs = [cert.strip().lower() for cert in job_profile.required_certifications.split(',')]
        candidate_certs = [cert.strip().lower() for cert in candidate_obj.certifications.split(',')]

        if not required_certs:
            return 0.5

        match_count = sum(1 for cert in required_certs if cert in candidate_certs)
        return match_count / len(required_certs)

    def _calculate_personality_score(self, candidate_obj: candidate.Candidate, job_profile: job.Job) -> float:
        """Calculate personality match score."""
        if not job_profile.required_personality_traits:
            return 0.5

        try:
            required_traits = json.loads(job_profile.required_personality_traits)
        except:
            return 0.5

        # Prefer test results over CV analysis if available
        if candidate_obj.test_personality_traits:
            try:
                candidate_traits = json.loads(candidate_obj.test_personality_traits)
            except:
                candidate_traits = {}
        elif candidate_obj.personality_traits:
            try:
                candidate_traits = json.loads(candidate_obj.personality_traits)
            except:
                candidate_traits = {}
        else:
            return 0.5

        if not required_traits or not candidate_traits:
            return 0.5

        # Calculate Euclidean distance between required and candidate traits
        distance = 0
        for trait in required_traits:
            required_value = required_traits.get(trait, 0.5)
            candidate_value = candidate_traits.get(trait, 0.5)
            distance += (required_value - candidate_value) ** 2

        distance = math.sqrt(distance)

        # Convert distance to a similarity score (0 to 1)
        # Max possible distance is sqrt(5) for 5 traits, so we normalize
        max_distance = math.sqrt(5)
        similarity = 1 - (distance / max_distance)

        return similarity