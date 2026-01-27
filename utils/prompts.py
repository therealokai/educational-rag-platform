"""Centralized prompts used across the project.

Place all long prompt strings here so they can be reused and maintained in one place.
"""

VISUAL_ANALYST_PROMPT = (
    "You are a helpful visual analyst and educational professor. You will receive an image (PNG, base64 encoded) "
    "representing a PDF page of a book that may contain graphs, charts, tables, mathematical "
    "equations, or other visual data. Provide a JSON object with two keys:\n"
    "1) summary: a 1-2 sentence concise summary suitable for embedding.\n"
    "2) details: a detailed description of all visual elements (chart types, axes labels, "
    "data trends, notable values, tables, equations including variable names and meanings), "
    "and any suggestions for extracting structured values. Also perform OCR to extract any visible text.\n"
    "Return only valid JSON."
)


# Generator prompt template for MCQs. Use .format(remaining=..., context=..., query=...)
MCQ_GENERATOR_PROMPT = (
    "You are an expert educator. Based on the following context, generate exactly {remaining} "
    "Multiple Choice Questions (MCQs).\n\n"
    "Context: {context}\n"
    "Topic/Query: {query}\n\n"
    "Produce only MCQs. For each MCQ include 4 options labeled A) through D) and indicate the correct answer.\n"
    "Return the questions as a JSON array of strings exactly, for example:\n"
    "[\"What is X? A) ... B) ... C) ... D) ... Answer: B\", \"What is Y? A) ... B) ... C) ... D) ... Answer: A\"]\n\n"
    "Each string must contain the question text, the four options, and the answer as shown above. "
    "Do not include any additional text outside the JSON array."
)


# Evaluator prompt template. Use .format(context=..., questions_json=...)
EVALUATOR_PROMPT = (
    "You are a strict quality controller for educational content.\n\n"
    "Context: {context}\n"
    "Candidate questions (JSON array): {questions_json}\n\n"
    "For each candidate question, determine if it is accurate and pedagogically sound according to the context.\n"
    "Return a JSON object with these fields:\n"
    "{{\n  \"passed_questions\": [ ... ],   # array of question strings that are acceptable\n"
    "  \"failed\": [ ... ],            # array of question strings that failed\n"
    "  \"evaluation\": \"...\"          # human-readable summary\n}}\n\n"
    "Only return valid JSON."
)
