"""
Certification Module

Provides certification tracking and milestone management for FLL-Sim educational progress.
"""
from src.fll_sim.utils.logger import FLLLogger

class CertificationManager:
    """Manages user certifications and milestones."""
    def __init__(self):
        self.logger = FLLLogger('CertificationManager')
        self.certifications = {}

    def award_certification(self, user_id, cert_name):
        self.certifications.setdefault(user_id, []).append(cert_name)
        self.logger.info(f"Awarded certification {cert_name} to user {user_id}")

    def get_certifications(self, user_id):
        return self.certifications.get(user_id, [])

    def has_certification(self, user_id, cert_name):
        return cert_name in self.certifications.get(user_id, [])
