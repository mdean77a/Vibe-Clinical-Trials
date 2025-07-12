"""
Generation prompts for document generation workflows.

These prompts are used for the actual LLM messages during document generation.
"""

# Human message prompt template for section generation
SECTION_GENERATION_PROMPT = "Context: {context}\n\nGenerate the {section_name} section."
