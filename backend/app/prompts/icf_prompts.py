"""
ICF (Informed Consent Form) prompts for document generation.

These prompts guide the LLM in generating each section of an ICF document
according to FDA 21 CFR 50 guidelines.
"""

ICF_PROMPTS = {
    "summary": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate a brief, focused summary (2-3 paragraphs maximum) that:
- States the study's primary purpose in one clear sentence
- Briefly describes the main intervention or treatment being tested
- Mentions the expected duration and number of visits
- Uses simple, plain language (8th grade reading level)
- Follows FDA 21 CFR 50 guidelines
Focus on the most essential information only.
""",
    "background": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate content that:
- Explains the medical condition or research question
- Describes why this study is needed
- Summarizes relevant previous research
- Explains how this study will advance knowledge
- Uses clear, non-technical language when possible
- Follows FDA 21 CFR 50 guidelines
""",
    "participants": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading. This section generally will not require more than 200 to 300 words.
Generate content restricted to the following:
- States where the study is being conducted (for example, at this hospital, or in a network, or in multiple hospitals)
- Explains the funding source for the study (often the NIH) - but do not include the funding legislation, fiscal year, etc.  Just name the funding agency.
- States the total number of participants expected to enroll in the study
- Explains the total period of time that the study is expected to enroll subjects.
Do not include inclusion or exclusion criteria as these are handled in other sections of the document.
Do not include any content about eligibility, and do not include content about randomization or study procedures.  These are handled in other sections of the document.
""",
    "procedures": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate content that:
- Lists all study visits and procedures chronologically
- Explains what happens at each visit
- Describes any tests, treatments, or interventions 
- Mentions time commitments for each procedure
- Explains any follow-up requirements
- Uses step-by-step format for clarity
- Follows FDA 21 CFR 50 guidelines
""",
    "alternatives": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate content that:
- Lists available alternative treatments outside the study
- Explains standard care options
- Describes pros and cons of alternatives vs. study participation
- Mentions that choosing not to participate is an alternative
- Uses non-coercive language
- Follows FDA 21 CFR 50 guidelines
""",
    "risks": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate content that:
- Lists all known and potential risks
- Explains likelihood and severity of each risk
- Describes how risks will be monitored and managed
- Mentions unknown risks may exist
- Uses clear, honest language without minimizing risks
- Groups risks by category (common, serious, unknown)
- Follows FDA 21 CFR 50 guidelines
""",
    "benefits": """
You are an expert clinical trial specialist writing ICF content.
Write the section content directly without any preamble, introduction, or section title.
Do not include a heading.
Generate content that:
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
    "summary": "study purpose objectives primary secondary endpoints trial design intervention overview",
    "background": "background rationale medical condition disease previous studies literature review justification",
    "participants": "participating institutions, number of participants target enrollment, funding agency",
    "procedures": "study procedures visits tests treatments interventions timeline schedule follow-up assessments",
    "alternatives": "alternative treatments standard care options therapy comparisons current practice",
    "risks": "risks side effects adverse events safety monitoring toxicity complications contraindications",
    "benefits": "benefits outcomes efficacy potential improvements therapeutic effects clinical benefits",
}
