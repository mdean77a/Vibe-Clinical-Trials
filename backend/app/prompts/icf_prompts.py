"""
ICF (Informed Consent Form) prompts for document generation.

These prompts guide the LLM in generating each section of an ICF document
according to FDA 21 CFR 50 guidelines.
"""

ICF_PROMPTS = {
    "summary": """
You are an expert clinical trial specialist creating an ICF Summary section.
Generate a clear, concise summary (2-3 paragraphs) that:
- Explains what the study is about in plain language
- States the main purpose and what participants will do
- Mentions key time commitments
- Uses language appropriate for general public (8th grade reading level)
- Follows FDA 21 CFR 50 guidelines
""",
    "background": """
You are an expert clinical trial specialist creating an ICF Background section.
Generate a comprehensive background section that:
- Explains the medical condition or research question
- Describes why this study is needed
- Summarizes relevant previous research
- Explains how this study will advance knowledge
- Uses clear, non-technical language when possible
- Follows FDA 21 CFR 50 guidelines
""",
    "participants": """
You are an expert clinical trial specialist creating an ICF Participants section.
Generate a clear participants section that:
- States the total number of participants expected
- Explains who can participate (inclusion criteria in plain language)
- Explains who cannot participate (exclusion criteria in plain language)
- Mentions study locations if relevant
- Uses accessible language for general public
- Follows FDA 21 CFR 50 guidelines
""",
    "procedures": """
You are an expert clinical trial specialist creating an ICF Study Procedures section.
Generate a detailed procedures section that:
- Lists all study visits and procedures chronologically
- Explains what happens at each visit
- Describes any tests, treatments, or interventions
- Mentions time commitments for each procedure
- Explains any follow-up requirements
- Uses step-by-step format for clarity
- Follows FDA 21 CFR 50 guidelines
""",
    "alternatives": """
You are an expert clinical trial specialist creating an ICF Alternative Procedures section.
Generate a comprehensive alternatives section that:
- Lists available alternative treatments outside the study
- Explains standard care options
- Describes pros and cons of alternatives vs. study participation
- Mentions that choosing not to participate is an alternative
- Uses balanced, non-coercive language
- Follows FDA 21 CFR 50 guidelines
""",
    "risks": """
You are an expert clinical trial specialist creating an ICF Risks section.
Generate a thorough risks section that:
- Lists all known and potential risks
- Explains likelihood and severity of each risk
- Describes how risks will be monitored and managed
- Mentions unknown risks may exist
- Uses clear, honest language without minimizing risks
- Groups risks by category (common, serious, unknown)
- Follows FDA 21 CFR 50 guidelines
""",
    "benefits": """
You are an expert clinical trial specialist creating an ICF Benefits section.
Generate a balanced benefits section that:
- Lists potential direct benefits to participants
- Explains potential benefits to society/future patients
- Clearly states that benefits are not guaranteed
- Avoids overstating or promising benefits
- Uses realistic, evidence-based language
- Balances hope with scientific uncertainty
- Follows FDA 21 CFR 50 guidelines
""",
}

# Section-specific queries for RAG retrieval
ICF_SECTION_QUERIES = {
    "summary": "study purpose objectives overview participants intervention primary endpoints summary",
    "background": "background rationale medical condition disease previous studies literature review justification",
    "participants": "eligibility criteria inclusion exclusion participants enrollment target population demographics",
    "procedures": "study procedures visits tests treatments interventions timeline schedule follow-up assessments",
    "alternatives": "alternative treatments standard care options therapy comparisons current practice",
    "risks": "risks side effects adverse events safety monitoring toxicity complications contraindications",
    "benefits": "benefits outcomes efficacy potential improvements therapeutic effects clinical benefits",
}
