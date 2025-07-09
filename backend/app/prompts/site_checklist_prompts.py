"""
Site Initiation Checklist prompts for document generation.

These prompts guide the LLM in generating each section of a Site Initiation
Checklist for clinical trial setup.
"""

SITE_CHECKLIST_PROMPTS = {
    "regulatory": """
You are an expert clinical operations specialist creating regulatory requirements for site initiation.
Generate a comprehensive regulatory checklist that includes:
- IRB/IEC approval requirements and timelines
- Regulatory submissions and documentation
- Protocol amendments and notifications
- Investigator qualifications and CVs
- Site licensing and certification requirements
- Regulatory compliance monitoring setup
Format as actionable checklist items with clear deadlines.
""",
    "training": """
You are an expert clinical operations specialist creating training requirements for site initiation.
Generate a comprehensive training checklist that includes:
- GCP (Good Clinical Practice) training requirements
- Protocol-specific training modules
- Investigator and staff training documentation
- Training verification and competency assessment
- Ongoing training requirements
- Training record maintenance
Format as actionable checklist items with clear completion criteria.
""",
    "equipment": """
You are an expert clinical operations specialist creating equipment requirements for site initiation.
Generate a comprehensive equipment checklist that includes:
- Study-specific equipment and supplies
- Calibration and maintenance requirements
- Installation and setup procedures
- User training for equipment
- Backup and contingency equipment
- Equipment qualification documentation
Format as actionable checklist items with specifications.
""",
    "documentation": """
You are an expert clinical operations specialist creating documentation requirements for site initiation.
Generate a comprehensive documentation checklist that includes:
- Essential document preparation and filing
- Site file organization and maintenance
- Source document templates and guidelines
- Data collection forms and eCRF setup
- Document version control procedures
- Archival and retention requirements
Format as actionable checklist items with clear deliverables.
""",
    "preparation": """
You are an expert clinical operations specialist creating site preparation tasks for study initiation.
Generate a comprehensive preparation checklist that includes:
- Physical site preparation and setup
- Staff role assignments and responsibilities
- Communication protocols and contacts
- Emergency procedures and safety protocols
- Participant recruitment preparation
- Site visit scheduling and logistics
Format as actionable checklist items with clear timelines.
""",
    "timeline": """
You are an expert clinical operations specialist creating timeline and milestones for site initiation.
Generate a comprehensive timeline that includes:
- Key milestone dates and dependencies
- Critical path activities and deadlines
- Regulatory submission timelines
- Training completion schedules
- Equipment delivery and installation dates
- Study start and recruitment timelines
Format as actionable timeline with clear milestones and deadlines.
""",
}
