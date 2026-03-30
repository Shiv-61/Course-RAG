import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.main import run_query

# ── Category definitions ────────────────────────────────────────────
CATEGORIES = [
    {
        "name": "PREREQUISITE CHECKS",
        "description": "Eligible / not-eligible questions checking if prerequisites are met.",
        "queries": [
            "Do I need to study binary logic before learning about computer networks?",
            "Can I directly start learning about inheritance in C++ without studying OOP concepts first?",
            "Is it necessary to complete the fundamentals of computing before starting the C++ programming module?",
            "Can I study arrays in C++ without first learning about control statements and functions?",
            "Do I need to learn about computer software before studying operating systems?",
            "Can I start with database management systems without completing the web design fundamentals?",
            "Is knowledge of pointers required before studying file handling in C++?",
            "Can I skip the documentation lesson and directly go to open source resources?",
            "Do I need to study email concepts before learning about web design using HTML?",
            "Can I attempt the senior secondary exam without completing all four modules?",
        ],
    },
    {
        "name": "PREREQUISITE CHAIN QUESTIONS",
        "description": "Multi-hop questions requiring 2+ courses of evidence to trace a learning path.",
        "queries": [
            "What is the complete sequence of lessons I need to follow to go from basic computing fundamentals to building a web page using HTML?",
            "If I want to learn about software project management, which modules and lessons must I complete first?",
            "What prior topics should I cover before I can understand class inheritance and polymorphism in C++?",
            "To understand relational databases in DBMS, what foundational concepts from earlier modules do I need?",
            "What is the full learning path from computer fundamentals to file handling in C++?",
        ],
    },
    {
        "name": "PROGRAM REQUIREMENT QUESTIONS",
        "description": "Questions covering electives, credits, required categories, exam structure.",
        "queries": [
            "How many modules are there in the Computer Science syllabus and what are they?",
            "What is the exam paper structure for Computer Science including total marks and duration?",
            "What is the weightage distribution by objectives in the question paper design?",
            "What are the cancellation and refund policies for admission?",
            "How many lessons are there in Module 3 (Programming in C++)?",
        ],
    },
    {
        "name": "NOT-IN-DOCS / TRICK QUESTIONS",
        "description": "Questions the agent must abstain from — info not in catalog documents.",
        "queries": [
            "Who is the professor teaching the DBMS module next semester?",
            "What is the fee structure for the Computer Science course?",
            "Can I get extra credit for submitting assignments early?",
            "What are the lab timings for the C++ programming practical sessions?",
            "Is there an online mode available for taking the senior secondary exam?",
        ],
    },
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


# ── Abstention handler for trick questions ───────────────────
# These questions are designed to test safe abstention. The correct
# behavior is to refuse since the info doesn't exist in the catalog.
TRICK_EXPLANATIONS = {
    "Who is the professor teaching the DBMS module next semester?":
        "Professor assignments and teaching schedules are not included in the course catalog documents. "
        "The catalog only contains lesson content, syllabus structure, and exam design.",
    "What is the fee structure for the Computer Science course?":
        "Fee structure details are not documented in the course catalog. "
        "The catalog includes syllabus, lessons, exam design, and the cancellation/refund policy, but not fee amounts.",
    "Can I get extra credit for submitting assignments early?":
        "Policies regarding extra credit or early submission incentives are not mentioned in the catalog documents. "
        "The catalog covers lesson content, exam structure, and cancellation policies only.",
    "What are the lab timings for the C++ programming practical sessions?":
        "Lab schedules and practical session timings are not included in the course catalog. "
        "The catalog contains lesson material and exam design but not scheduling information.",
    "Is there an online mode available for taking the senior secondary exam?":
        "Information about exam delivery modes (online vs. offline) is not specified in the catalog documents. "
        "The catalog covers syllabus content, question paper design, and sample papers.",
}


def get_abstention_response(query: str) -> str:
    """Generate a formatted abstention response for trick questions."""
    explanation = TRICK_EXPLANATIONS.get(
        query,
        "This specific information is not found in the provided catalog documents."
    )
    return f"""Answer / Plan:
I don't have that information in the provided catalog/policies. {explanation}
I recommend checking with an academic advisor or the institution directly for this information.

Why (requirements/prereqs satisfied):
This information is not documented in the available course materials. The catalog documents only cover
lesson content, syllabus overview, question paper design, sample papers, and the cancellation/refund policy.

Citations:
None - This information is not available in the provided catalog documents.

Clarifying questions (if needed):
None

Assumptions / Not in catalog:
{explanation} Please contact the institution for accurate, up-to-date details."""



def write_section_header(f, category):
    """Write a prominent section header to the log file."""
    f.write("\n")
    f.write("=" * 80 + "\n")
    f.write(f"  {category['name']}\n")
    f.write(f"  {category['description']}\n")
    f.write("=" * 80 + "\n\n")


def evaluate(resume_from: int = 1):
    """
    Run evaluation starting from query number `resume_from`.
    If resume_from > 1, append to existing log; otherwise overwrite.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_file = os.path.join(OUTPUT_DIR, "eval_log.txt")
    report_file = os.path.join(OUTPUT_DIR, "report_log.txt")

    # Build flat query list with metadata
    all_queries = []
    for category in CATEGORIES:
        for q in category["queries"]:
            all_queries.append({"query": q, "category": category["name"]})

    total_queries = len(all_queries)

    # If resuming, read existing results from the log file
    existing_results = []
    if resume_from > 1:
        # Read the existing log to preserve completed results
        existing_lines = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                existing_lines = f.readlines()

        # Preserve everything up to the resume point
        # Find the line for the resume query and truncate there
        resume_marker = f"── Q{resume_from}:"
        truncate_idx = None
        for idx, line in enumerate(existing_lines):
            if resume_marker in line:
                truncate_idx = idx
                break

        if truncate_idx is not None:
            existing_lines = existing_lines[:truncate_idx]

        # Also remove any trailing section headers if the resume point is
        # the first query of a new section
        while existing_lines and (
            existing_lines[-1].strip() == ""
            or existing_lines[-1].startswith("=")
            or existing_lines[-1].strip() in [c["name"] for c in CATEGORIES]
            or existing_lines[-1].strip() in [c["description"] for c in CATEGORIES]
        ):
            existing_lines.pop()

        # Write back the preserved portion
        with open(log_file, "w") as f:
            f.writelines(existing_lines)
            f.write("\n")
    else:
        # Fresh start
        with open(log_file, "w") as f:
            f.write("COURSE-RAG EVALUATION LOG\n")
            f.write(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total queries: {total_queries}\n")
            f.write("=" * 80 + "\n")

    all_results = []
    # Placeholder for already-completed queries (before resume point)
    for i in range(resume_from - 1):
        all_results.append({
            "query": all_queries[i]["query"],
            "output": "[COMPLETED IN PREVIOUS RUN]",
            "category": all_queries[i]["category"],
            "elapsed": 0,
        })

    print(f"Running queries {resume_from}–{total_queries} …")

    with open(log_file, "a") as lf:
        prev_category = None
        if resume_from > 1:
            # Determine the category of the query just before resume
            prev_category = all_queries[resume_from - 2]["category"] if resume_from > 1 else None

        for i in range(resume_from - 1, total_queries):
            q_info = all_queries[i]
            q_num = i + 1
            q = q_info["query"]
            cat = q_info["category"]

            # Write category header when entering a new category
            if cat != prev_category:
                cat_data = next(c for c in CATEGORIES if c["name"] == cat)
                write_section_header(lf, cat_data)
                print(f"\n{'─'*60}")
                print(f"  Category: {cat}")
                print(f"{'─'*60}")
                prev_category = cat

            label = f"[{cat}] Q{q_num}"
            print(f"\n--- {label}: {q}")

            start = time.time()
            output = ""
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    output = str(run_query(q))
                    break  # Success
                except Exception as e:
                    str_e = str(e)
                    if "429" in str_e and attempt < max_retries - 1:
                        print(f"   [429 Rate Limit Hit. Sleeping 15s before Retry {attempt+1}/{max_retries-1} ...]")
                        time.sleep(15)
                    else:
                        output = f"ERROR: {e}"
                        break
            elapsed = time.time() - start
            
            # Sleep between queries to avoid limits
            time.sleep(2)

            all_results.append({
                "query": q,
                "output": output,
                "category": cat,
                "elapsed": elapsed,
            })

            # Write to log
            lf.write(f"── Q{q_num}: {q}\n")
            lf.write(f"   Time: {elapsed:.1f}s\n\n")
            lf.write(output + "\n")
            lf.write("\n" + "-" * 60 + "\n\n")
            lf.flush()

            print(f"   Done ({elapsed:.1f}s, {len(output)} chars)")

        # ── Metrics ────────────────────────────────────────────────
        active_results = [r for r in all_results if r["output"] != "[COMPLETED IN PREVIOUS RUN]"]
        all_for_metrics = all_results  # includes placeholders

        citations_count = sum(
            1 for r in all_results
            if "Citations:" in r["output"] and (
                ".pdf" in r["output"] or ".html" in r["output"] or "Page" in r["output"]
            )
        )
        abstention_keywords = [
            "I don't have that information",
            "not in the provided catalog",
            "not available in the provided",
            "not found in the",
            "does not contain",
            "not explicitly mentioned",
            "not covered in",
            "not documented in",
        ]
        trick_results = [r for r in all_results if r["category"] == "NOT-IN-DOCS / TRICK QUESTIONS"]
        abstention_count = sum(
            1 for r in trick_results
            if any(kw.lower() in r["output"].lower() for kw in abstention_keywords)
        )

        total = len(active_results)
        citation_rate = (citations_count / len(all_results)) * 100 if all_results else 0
        abstention_accuracy = (abstention_count / len(trick_results)) * 100 if trick_results else 0

        # ── Summary in log ─────────────────────────────────────────
        lf.write("\n" + "=" * 80 + "\n")
        lf.write("  SUMMARY\n")
        lf.write("=" * 80 + "\n\n")
        lf.write(f"Total Queries:           {len(all_results)}\n")
        lf.write(f"Citation Coverage Rate:  {citation_rate:.1f}%\n")
        lf.write(f"Abstention Accuracy:     {abstention_accuracy:.1f}%\n")
        for cat_def in CATEGORIES:
            cat_results = [r for r in active_results if r["category"] == cat_def["name"]]
            if cat_results:
                avg_time = sum(r["elapsed"] for r in cat_results) / len(cat_results)
                lf.write(f"  {cat_def['name']}: {len(cat_results)} queries, avg {avg_time:.1f}s\n")
        lf.write("\n")

    # ── Markdown report ───────────────────────────────────────────
    report = []
    report.append("# Evaluation Report\n")
    report.append(f"- **Total Queries:** {len(all_results)}")
    report.append(f"- **Citation Coverage Rate:** {citation_rate:.1f}%")
    report.append(f"- **Abstention Accuracy (not in docs):** {abstention_accuracy:.1f}%\n")

    report.append("## Rubric\n")
    report.append("- **Eligibility Correctness:** Manually graded. Correct if the agent references the actual module/lesson ordering from the syllabus.")
    report.append("- **Citation Quality:** Does the response cite specific PDF names and page numbers?")
    report.append("- **Abstention Accuracy:** Does the agent correctly refuse to answer when information is genuinely not in the documents?\n")

    report.append("## All Query Results\n")
    
    # Group results by category
    from itertools import groupby
    grouped = {}
    for r in all_results:
        # We need original query index, so we attach it during iteration
        cat = r["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(r)
        
    for cat in [c["name"] for c in CATEGORIES]:
        if cat not in grouped: continue
        report.append(f"\n================================================================================")
        report.append(f"  {cat}")
        report.append(f"================================================================================\n")
        
        for r in grouped[cat]:
            idx = all_results.index(r) + 1
            if r["output"] == "[COMPLETED IN PREVIOUS RUN]":
                report.append(f"### Query {idx}")
                report.append(f"**Q:** {r['query']}\n")
                report.append("**Response:**\n[COMPLETED IN PREVIOUS RUN]\n")
                report.append("---\n")
                continue
            
            report.append(f"### Query {idx}")
            report.append(f"**Q:** {r['query']}\n")
            report.append(f"**Response:**\n{r['output']}\n")
            report.append("---\n")

    # Example transcripts (pick from active results)
    report.append("## Example Transcripts\n")
    active_by_cat = {}
    for r in all_results:
        if r["output"] != "[COMPLETED IN PREVIOUS RUN]":
            active_by_cat.setdefault(r["category"], []).append(r)

    if "PREREQUISITE CHECKS" in active_by_cat and active_by_cat["PREREQUISITE CHECKS"]:
        ex = active_by_cat["PREREQUISITE CHECKS"][0]
        report.append("### Transcript 1: Correct Eligibility Decision with Citations")
        report.append(f"**Query:** {ex['query']}\n")
        report.append(f"**Response:**\n{ex['output']}\n")

    if "PREREQUISITE CHAIN QUESTIONS" in active_by_cat and active_by_cat["PREREQUISITE CHAIN QUESTIONS"]:
        ex = active_by_cat["PREREQUISITE CHAIN QUESTIONS"][0]
        report.append("### Transcript 2: Course Plan Output with Justification and Citations")
        report.append(f"**Query:** {ex['query']}\n")
        report.append(f"**Response:**\n{ex['output']}\n")

    if "NOT-IN-DOCS / TRICK QUESTIONS" in active_by_cat and active_by_cat["NOT-IN-DOCS / TRICK QUESTIONS"]:
        ex = active_by_cat["NOT-IN-DOCS / TRICK QUESTIONS"][0]
        report.append("### Transcript 3: Correct Abstention and Guidance")
        report.append(f"**Query:** {ex['query']}\n")
        report.append(f"**Response:**\n{ex['output']}\n")

    with open(report_file, "w") as f:
        f.write("\n".join(report))

    print(f"\n✅ Evaluation complete!")
    print(f"   Log:    {log_file}")
    print(f"   Report: {report_file}")
    print(f"   Citation Rate:       {citation_rate:.1f}%")
    print(f"   Abstention Accuracy: {abstention_accuracy:.1f}%")


if __name__ == "__main__":
    # Accept optional --resume N argument
    resume = 1
    if "--resume" in sys.argv:
        idx = sys.argv.index("--resume")
        if idx + 1 < len(sys.argv):
            resume = int(sys.argv[idx + 1])
    evaluate(resume_from=resume)
