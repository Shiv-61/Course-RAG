import sys
from crewai import Crew, Process
from src.agents import get_intake_agent, get_retriever_agent, get_planner_agent, get_verifier_agent
from src.tasks import intake_task, retrieval_task, planning_task, verification_task

def run_query(student_query: str):
    # Initialize agents
    intake = get_intake_agent()
    retriever = get_retriever_agent()
    planner = get_planner_agent()
    verifier = get_verifier_agent()

    # Define tasks
    t_intake = intake_task(intake, student_query)
    t_retrieval = retrieval_task(retriever, student_query)
    t_planning = planning_task(planner)
    t_verification = verification_task(verifier)

    # Establish Crew
    crew = Crew(
        agents=[intake, retriever, planner, verifier],
        tasks=[t_intake, t_retrieval, t_planning, t_verification],
        process=Process.sequential,
        verbose=True
    )

    # Execute
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n--- Processing Query: {query} ---\n")
        output = run_query(query)
        print("\n=== FINAL ASSISTANT OUTPUT ===\n")
        print(output)
    else:
        print("Please provide a query as an argument.")
        print('Example: python -m src.main "Can I take CS301 if I have taken CS101?"')
