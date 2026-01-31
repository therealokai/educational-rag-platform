"""Centralized prompts used across the project.

Place all long prompt strings here so they can be reused and maintained in one place.
"""
TOC_TEXT_EXTRACTOR_PROMPT = """
You are a strict document parser.

You will receive raw extracted text from a book page that may contain a Table of Contents or Index.

Your job:
- Parse the provided text ONLY.
- Do NOT infer missing information.
- Do NOT use external knowledge.
- Do NOT guess chapter names, topics, or page numbers.
- If something is unclear, incomplete, or ambiguous, write null.
- Preserve original wording and spelling.

Return ONLY valid JSON with the following schema:

{{
  "is_table_of_contents": true | false,
  "entries": [
    {{
      "chapter_number": "string | null",
      "chapter_title": "string | null",
      "section_title": "string | null",
      "page_number": "string | null"
    }}
  ],
  "notes": "any uncertainty, truncation, or parsing ambiguity"
}}

Rules:
- If the text is NOT a table of contents or index, set is_table_of_contents = false and entries = [].
- Do not summarize or paraphrase.
- Do not normalize numbers or titles.
- Do not clean or correct typos.
- Return JSON only.

The raw extracted text from the page is:
{page_text}
"""


PAGE_CHUNK_TEXT_PROMPT = """
You are a strict educational document extractor.

You will receive:
1) Extracted raw text of a book page.
2) The extracted Table of Contents / Index (if available).

IMPORTANT TAXONOMY RULES:
- The hierarchy MUST be: Subject > Topic > Subtopic.
- Subject is the broad academic field (e.g., Math, Physics, Chemistry, Biology, History, Geography, Computer Science).
- Topic is the branch inside the subject (e.g., Algebra, Calculus, Geometry for Math).
- Subtopic is the specific lesson or section title (e.g., Simplifying Expressions).
- NEVER use a chapter name or section title as Subject.
- NEVER collapse Topic into Subject.
- Prefer TOC hierarchy over page titles.

Your job:
- Work ONLY with the provided text and TOC.
- Do NOT use any external knowledge.
- Do NOT correct mistakes in the source.
- Do NOT merge content from other pages.
- Map Subject → Topic → Subtopic using the TOC and page headings.
- If Subject cannot be determined with high confidence from TOC or page context, set subject = null.
- If Topic cannot be determined clearly, set topic_name = null and confidence = "uncertain".
- If Subtopic cannot be determined clearly, set subtopic_name = null and confidence = "uncertain".

DESCRIPTION RULES (VERY IMPORTANT):
- For each subtopic, the "description" must include ONLY the text in this page that is directly related to that subtopic.
- Do NOT include text belonging to other topics or subtopics.
- Do NOT summarize. Do NOT paraphrase. Do NOT add explanations.
- Preserve the original wording and formatting as much as possible.
- If the page contains ONLY ONE subtopic, then set the description to the FULL page text.
- If the page contains multiple subtopics, split the page text correctly between them based on section headings or clear boundaries.
- If boundaries are unclear, include only the text that most clearly belongs to the subtopic and mention uncertainty in confidence.

Return ONLY valid JSON with this schema:

{{
  "subject": "string | null",
  "topics": [
    {{
      "topic_name": "string | null",
      "confidence": "high | medium | low | uncertain",
      "subtopics": [
        {{
          "subtopic_name": "string | null",
          "confidence": "high | medium | low | uncertain",
          "description": "ALL and ONLY the text from this page related to this subtopic"
        }}
      ]
    }}
  ]
}}

Hard Rules:
- Do not invent subtopics not present in the page or TOC.
- Do not split content into artificial subtopics.
- Do not infer missing hierarchy.
- Do not use general knowledge to decide where text belongs.
- Return JSON only.

The extracted table of contents / index is:
{toc_json}

Extracted raw text of the page is:
{page_text}
"""























TOC_EXTRACTOR_PROMPT = """
You are a strict document parser. 
You will receive an image of a book page that may contain a Table of Contents or Index.

Your job:
- Perform OCR on ALL visible text.
- Extract ONLY what is explicitly visible in the image.
- Do NOT infer, guess, or complete missing information.
- If something is unclear or cut, write null.
- Do NOT use external knowledge.
- Do NOT assume chapter names, topics, or page numbers unless clearly visible.

Return ONLY valid JSON with the following schema:

{{
  "raw_ocr_text": "full OCR text exactly as seen on the page",
  "is_table_of_contents": true | false,
  "entries": [
    {{
      "chapter_number": "string | null",
      "chapter_title": "string | null",
      "section_title": "string | null",
      "page_number": "string | null"
    }}
  ],
  "notes": "any uncertainty, truncation, or unreadable parts"
}}

Rules:
- If this page is NOT a table of contents or index, set is_table_of_contents = false and entries = [].
- Preserve original wording and spelling.
- Do not summarize or paraphrase.
- Do not invent structure.
"""

PAGE_CHUNK_PROMPT = """
You are a strict educational document extractor.

You will receive:
1) An image of a book page.
2) The extracted Table of Contents / Index from earlier pages.

Your job:
- Perform OCR on the page.
- Describe all visual elements (graphs, tables, diagrams, equations).
- Map this page to subject / topic / subtopic ONLY if it is explicitly stated or clearly referenced by the page content or TOC.
- If subject/topic/subtopic is not clearly inferable from the page or index, set them to null.
- DO NOT guess.
- DO NOT use outside knowledge.
- DO NOT rewrite concepts using your own knowledge.
- If something is ambiguous, mark it as "uncertain".
- If the page contains formulas, extract them in LaTeX format if visible.
- The canonical_text must be fully grounded in the page content only.

Return ONLY valid JSON with this schema:

{{
  "page_ocr_text": "full OCR text exactly as seen",
  "subject": "string | null",
  "topics": [
    {{
      "topic_name": "string | null",
      "confidence": "high | medium | low | uncertain",
      "subtopics": [
        {{
          "subtopic_name": "string | null",
          "confidence": "high | medium | low | uncertain"
        }}
      ]
    }}
  ],
  "visual_elements": [
    {{
      "type": "graph | table | diagram | equation | image | other",
      "description": "precise visual description grounded in the image",
      "structured_values": "any extractable numeric values or labels, or null"
    }}
  ],
  "equations_latex": [
    {{
      "latex": "string",
      "description": "plain-language description of what the equation represents based only on page content"
    }}
  ],
  "canonical_text": "A faithful textual representation of what is on the page (OCR text + visual descriptions). Do NOT add new information.",
  "grounding_warnings": [
    "List any part where information was unclear, truncated, or partially unreadable"
  ]
}}

Hard Rules:
- If the page does not mention a topic or subtopic explicitly, set them to null.
- Do not merge concepts from different pages.
- Do not introduce definitions not present in the image.
- Do not correct the author's mistakes.
- The canonical_text must not contain any knowledge not present in OCR or visual description.

The extracted table of contents / index is:
{toc_json}
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
