"""
Prompts package for clinical trial document generation.

This package contains prompt templates for various document types:
- ICF (Informed Consent Form) prompts
- Site Initiation Checklist prompts
- Generation prompts for LLM messages
"""

from .generation_prompts import SECTION_GENERATION_PROMPT
from .icf_prompts import ICF_PROMPTS
from .site_checklist_prompts import SITE_CHECKLIST_PROMPTS

__all__ = ["ICF_PROMPTS", "SITE_CHECKLIST_PROMPTS", "SECTION_GENERATION_PROMPT"]
