from crewai import Task
from textwrap import dedent

def intake_task(agent, user_query):
    return Task(
        description=dedent(f"""
            Analyze the following student query:
            "{user_query}"
            
            Step 1: Determine query type:
            - KNOWLEDGE QUERY: if the student is asking about a concept, definition, topic explanation
              (e.g., "what is DBMS?", "explain inheritance in C++", "importance of networking")
            - PLANNING QUERY: if the student is asking about prerequisites, eligibility, or course plans
              (e.g., "can I take CS301?", "plan my next semester")
            
            Step 2:
            - For KNOWLEDGE QUERY: Simply pass the question forward for catalog retrieval. No student profile needed.
            - For PLANNING QUERY: Extract completed courses, grades, target major, target term, max credits.
              Identify what information is missing.
            
            Output your classification and prepared query.
        """),
        expected_output="Query type classification (KNOWLEDGE or PLANNING) and the prepared query for retrieval.",
        agent=agent
    )

def retrieval_task(agent, user_query):
    return Task(
        description=dedent(f"""
            Based on the student query:
            "{user_query}"
            
            Use your Catalog Retrieval Tool to search the vector database for relevant information.
            
            For KNOWLEDGE queries: Search for definitions, explanations, concepts, and detailed content.
            For PLANNING queries: Search for prerequisites, co-requisites, program requirements, and policies.
            
            CRITICAL INSTRUCTIONS:
            1. Use the tool to search with the EXACT user query first.
            2. If needed, also search with related terms to get comprehensive results.
            3. CRITICAL: You have a STRICT token limit. In your output, DO NOT return the massive raw text chunks. Instead, extract only the sentences answering the question, paired with their exact Source (Document + Page Number).
            4. Keep your output extremely concise, max 200 words.
            5. If the catalog does not contain relevant information, state "Not in catalog. Proceed with LLM knowledge if applicable."
        """),
        expected_output="Extracted facts and sources from the relevant catalog chunks, heavily summarized to save tokens.",
        agent=agent
    )

def planning_task(agent):
    return Task(
        description=dedent("""
            Using the retrieved catalog information from the Retriever Agent, construct a comprehensive answer.
            
            For KNOWLEDGE QUERIES:
            - Synthesize the retrieved content into a clear, detailed answer.
            - Include specific facts, definitions, and explanations directly from the retrieved text.
            - Cite the source document and page for every fact.
            - If the retrieved content does not contain the answer, you MAY use your internal general knowledge to answer, but clearly state that this is from general knowledge and not the catalog.
            
            For PLANNING QUERIES:
            - Determine eligibility based on prerequisites found in the retrieved content.
            - Propose course plans with justification per course.
            - Note any risks/assumptions.
            
            IMPORTANT: Try to base your answer strictly on the retrieved text when available. If not, fallback to internal knowledge but mark it as such.
        """),
        expected_output="A comprehensive, well-cited answer that directly uses the retrieved catalog content.",
        agent=agent
    )

def verification_task(agent):
    return Task(
        description=dedent("""
            Audit the response from the Planner/Knowledge Expert. Check:
            
            1. Does the answer prioritize the retrieved content?
            2. Does every factual claim from the catalog have a source citation (document name + page)?
            3. Does the answer directly address the user's question?
            4. If the documents genuinely don't contain the answer, allow the Planner's answer if it used general knowledge, but ensure it is clearly marked as "Not in catalog (General Knowledge)".
            
            CRITICAL: You are operating under a strict 500 token limit. You MUST be extremely concise. Get straight to the point. DO NOT write long paragraphs. Use bullet points where possible.
            
            Format the FINAL output in this EXACT structure (keep each section very brief!):
            
            Answer / Plan:
            [Very brief direct answer or course plan]
            
            Why (requirements/prereqs satisfied):
            [1-2 sentences max justification]
            
            Citations:
            [Doc Name (Page X)]
            
            Clarifying questions (if needed):
            [Write "None" or max 1-2 brief questions]
            
            Assumptions / Not in catalog:
            [Brief assumption statement or "None"]
        """),
        expected_output="The final audited response in the exact 5-part mandatory format, formatted EXTREMELY concisely with proper citations.",
        agent=agent
    )
