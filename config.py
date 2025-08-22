import os
from dataclasses import dataclass

@dataclass
class Settings:
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    N8N_AGENT_A_URL: str = os.getenv('N8N_AGENT_A_URL', 'https://primary-production-8d313.up.railway.app/webhook/message')
    N8N_AGENT_B_URL: str = os.getenv('N8N_AGENT_B_URL', 'https://primary-production-8d313.up.railway.app/webhook/message')
    N8N_AGENT_C_URL: str = os.getenv('N8N_AGENT_C_URL', 'https://primary-production-8d313.up.railway.app/webhook/message')

    def _auth_header(env_key_name: str):
        raw = os.getenv(env_key_name)
        if not raw:
            return None
        parts = [p.strip() for p in raw.split(',') if ':' in p]
        return {k.strip(): v.strip() for k, v in (p.split(':', 1) for p in parts)}

    # N8N_AGENT_A_AUTH = _auth_header.__func__('N8N_AGENT_A_AUTH')
    # N8N_AGENT_B_AUTH = _auth_header.__func__('N8N_AGENT_B_AUTH')
    # N8N_AGENT_C_AUTH = _auth_header.__func__('N8N_AGENT_C_AUTH')

settings = Settings()
