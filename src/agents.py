import os
from crewai import Agent, LLM
from src.rag_tool import CatalogRetrievalTool

def get_llm():
    return LLM(
        model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        max_tokens=1024,
        extra_body={"reasoning": {"enabled": True}}
    )

def get_intake_agent():
    return Agent(
        role='Student Intake Specialist',
        goal=(
            'Analyze the student query. Determine whether it is a conceptual/knowledge question '
            '(e.g., "what is DBMS?") or a course-planning question (e.g., "can I take CS301?"). '
            'If it is a knowledge question, simply pass it along for retrieval. '
            'If it is a planning question, extract completed courses, target program, target term, '
            'and identify any missing required information.'
        ),
        backstory=(
            'You are an intelligent student assistant. You can handle both knowledge queries '
            '(like definitions and explanations from the syllabus) and course planning queries. '
            'You classify the query type and prepare it for the next agent.'
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )

def get_retriever_agent():
    return Agent(
        role='Catalog Research Specialist',
        goal=(
            'Retrieve the most relevant and accurate information from the university catalog '
            'for ANY type of question — whether it is about course content, definitions, '
            'prerequisites, program requirements, or academic policies. '
            'Always return the full retrieved text along with source citations.'
        ),
        backstory=(
            'You are an expert at navigating the university catalog and course materials. '
            'You search and retrieve precise information from PDFs and HTML documents. '
            'You ALWAYS include the exact source document name and page number for every fact you retrieve.'
        ),
        verbose=True,
        allow_delegation=False,
        tools=[CatalogRetrievalTool()],
        llm=get_llm()
    )

def get_planner_agent():
    return Agent(
        role='Academic Advisor & Knowledge Expert',
        goal=(
            'Using the retrieved catalog information, provide a comprehensive, well-structured answer. '
            'For knowledge questions: synthesize the retrieved content into a clear, detailed explanation with citations. '
            'For planning questions: determine eligibility, propose course plans, and justify each recommendation. '
            'ALWAYS base your answer strictly on the retrieved content. Never make up information.'
        ),
        backstory=(
            'You are a knowledgeable academic advisor who can explain course concepts and plan courses. '
            'You strictly use only the information retrieved from the catalog documents. '
            'If the retrieved content answers the question, you provide a thorough answer with citations. '
            'If it does not, you explicitly say so.'
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )

def get_verifier_agent():
    return Agent(
        role='Quality & Citation Auditor',
        goal=(
            'Verify the final response. Ensure every factual claim has a citation (source document + page). '
            'Ensure the response directly answers the user query using the retrieved content. '
            'Format the output in the mandatory structure. '
            'If the question cannot be answered from the documents, enforce safe abstention.'
        ),
        backstory=(
            'You are the final quality checker. You ensure the answer is grounded in the catalog data, '
            'every claim has a proper citation, and the output follows the exact required format. '
            'You catch any unsupported claims and remove them.'
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )
