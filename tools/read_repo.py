import csv
from firestore import read_all_in_collection

def query_and_analyze_documents(collection_name):
    """
    Queries Firestore documents, filters them, and extracts structured data for analysis.

    Args:
        collection_name (str): The name of your Firestore collection.

    Returns:
        list: A list of dictionaries, where each dictionary contains the extracted
              and structured data for a valid document.
    """
    results = []
    try:
        all_docs = read_all_in_collection(collection_name)

        for doc_data in all_docs:
            # 1. Filter out documents without content in region_tags
            #    and with minimal evaluation data
            if not doc_data.get("region_tags") or \
               not isinstance(doc_data["region_tags"], list) or \
               len(doc_data["region_tags"]) == 0 or \
               not doc_data.get("evaluation_data") or \
               not doc_data["evaluation_data"].get("criteria_breakdown") or \
               not isinstance(doc_data["evaluation_data"]["criteria_breakdown"], list) or \
               len(doc_data["evaluation_data"]["criteria_breakdown"]) == 0:
                print(f"Skipping document {doc_data.get('id', 'unknown')} due to missing region_tags or minimal evaluation data.")
                continue

            # Extract top-level fields
            evaluation_date = doc_data.get("evaluation_date")
            git_info = doc_data.get("git_info", {})
            evaluation_data = doc_data.get("evaluation_data", {})
            region_tags = doc_data.get("region_tags", [])
            github_link = git_info.get("github_link")
            last_updated = git_info.get("last_updated")
            github_repo = git_info.get("github_repo")

            overall_compliance_score = evaluation_data.get("overall_compliance_score")
            identified_generic_problem_categories = evaluation_data.get("identified_generic_problem_categories", [])

            # Extract scores from criteria_breakdown
            runnability_score = None
            api_effectiveness_score = None
            comments_code_clarity_score = None
            formatting_score = None
            language_score = None

            criteria_breakdown = evaluation_data.get("criteria_breakdown", [])
            for criterion in criteria_breakdown:
                criterion_name = criterion.get("criterion_name")
                score = criterion.get("score")
                if criterion_name == "Runnability & Configuration":
                    runnability_score = score
                elif criterion_name == "API Effectiveness (googleapis/googleapis)":
                    api_effectiveness_score = score
                elif criterion_name == "Comments & Code Clarity":
                    comments_code_clarity_score = score
                elif criterion_name == "Formatting & Consistency":
                    formatting_score = score
                elif criterion_name == "Language Best Practices":
                    language_score = score

            # Structure the extracted data
            structured_doc = {
                "region_tags": ", ".join(region_tags), 
                "evaluation_date": evaluation_date,
                "github_link": github_link,
                "last_updated": last_updated,
                "github_repo": github_repo,
                "runnability_score": runnability_score,
                "api_effectiveness_score": api_effectiveness_score,
                "comments_code_clarity_score": comments_code_clarity_score,
                "formatting_score": formatting_score,
                "language_score": language_score,
                "overall_compliance_score": overall_compliance_score,
                "identified_generic_problem_categories": ", ".join(identified_generic_problem_categories), # Convert list to string
            }
            results.append(structured_doc)

    except Exception as e:
        print(f"An error occurred: {e}")

    return results

if __name__ == "__main__":
    # Replace 'your_collection_name' with the actual name of your Firestore collection
    # And ensure your Google Cloud credentials are set up (e.g., GOOGLE_APPLICATION_CREDENTIALS environment variable)
    collection = "Python"
    analyzed_data = query_and_analyze_documents(collection)

    csv_file_path = "output.csv"

    if analyzed_data:
        # Get headers from the first dictionary
        headers = analyzed_data[0].keys()

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(analyzed_data)
        print(f"\nSuccessfully wrote {len(analyzed_data)} documents to {csv_file_path}")
    else:
        print("\nNo documents to write to CSV.")

    print(f"\nTotal documents analyzed: {len(analyzed_data)}")
