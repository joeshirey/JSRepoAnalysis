import re
from collections import OrderedDict
# You will need to install your preferred LLM library, e.g.:
# pip install --upgrade google-cloud-aiplatform
# from vertexai.generative_models import GenerativeModel

# ==============================================================================
# 1. THE HIERARCHY AND KEYWORD MAPPING (BRAIN OF THE RULES ENGINE)
# ==============================================================================
# This dictionary maps keywords to their official product category and name.
# Keywords are lowercase for case-insensitive matching.

PRODUCT_HIERARCHY = {
    # AI and Machine Learning
    ('AI and Machine Learning', 'Vertex AI'): ['vertex-ai', 'vertexai', 'aiplatform', 'gemini', 'imagen', 'gemma', 'cmle'],
    ('AI and Machine Learning', 'Natural Language API'): ['language', 'naturallanguage'],
    ('AI and Machine Learning', 'Translation API'): ['translate'],
    ('AI and Machine Learning', 'Vision AI'): ['vision', 'visualinspection'],
    ('AI and Machine Learning', 'Video Intelligence API'): ['video-intelligence', 'videointelligence'],
    ('AI and Machine Learning', 'Speech-to-Text'): ['speech'],
    ('AI and Machine Learning', 'Text-to-Speech'): ['tts', 'texttospeech'],
    ('AI and Machine Learning', 'AutoML'): ['automl'],
    ('AI and Machine Learning', 'Contact Center AI'): ['contact-center-ai', 'contactcenterinsights'],
    ('AI and Machine Learning', 'Document AI'): ['document-ai', 'documentai'],
    ('AI and Machine Learning', 'Talent Solution'): ['jobs', 'talent'],
    ('AI and Machine Learning', 'Model Armor'): ['model-armor', 'modelarmor'],

    # API Management
    ('API Management', 'Apigee'): ['apigee'],
    ('API Management', 'Endpoints'): ['endpoints'],

    # Compute
    ('Compute', 'App Engine'): ['appengine', r'\bgae\b'],
    ('Compute', 'Cloud Functions'): ['functions'],
    ('Compute', 'Cloud Run'): ['run'],
    ('Compute', 'Cloud TPU'): ['tpu'],
    ('Compute', 'Compute Engine'): ['compute', r'\bgce\b', 'vm_instance'],
    ('Containers', 'Google Kubernetes Engine (GKE)'): ['gke', 'kubernetes-engine', 'container'],
    ('Compute', 'Batch'): ['batch'],

    # Databases
    ('Databases', 'AlloyDB'): ['alloydb'],
    ('Databases', 'Bigtable'): ['bigtable'],
    ('Databases', 'Cloud SQL'): ['cloud-sql', 'cloudsql'],
    ('Databases', 'Datastore'): ['datastore'],
    ('Databases', 'Firestore'): ['firestore'],
    ('Databases', 'Spanner'): ['spanner'],
    ('Databases', 'Memorystore'): ['memorystore'],

    # Data Analytics
    ('Data Analytics', 'BigQuery'): ['bigquery', 'bqml'],
    ('Data Analytics', 'BigLake'): ['biglake'],
    ('Data Analytics', 'Composer'): ['composer'],
    ('Data Analytics', 'Dataflow'): ['dataflow'],
    ('Data Analytics', 'Dataproc'): ['dataproc'],
    ('Data Analytics', 'Looker'): ['looker'],
    ('Data Analytics', 'Pub/Sub'): ['pubsub'],

    # Developer Tools
    ('Developer Tools', 'Artifact Registry'): ['artifact-registry', 'artifactregistry'],
    ('Developer Tools', 'Cloud Build'): ['cloud-build', 'cloudbuild'],
    ('Developer Tools', 'Cloud Scheduler'): ['cloud-scheduler', 'cloudscheduler'],
    ('Developer Tools', 'Cloud Tasks'): ['cloud-tasks', 'tasks'],
    ('Developer Tools', 'Container Analysis'): ['container-analysis', 'containeranalysis'],

    # Management & Observability
    ('Management & Observability', 'Cloud Asset Inventory'): ['asset'],
    ('Management & Observability', 'Cloud Logging'): ['logging'],
    ('Management & Observability', 'Cloud Monitoring'): ['monitoring'],
    ('Management & Observability', 'Cloud Profiler'): ['profiler'],
    ('Management & Observability', 'Cloud Trace'): ['trace', 'opencensus', 'opentelemetry'],
    ('Management & Observability', 'Error Reporting'): ['error-reporting', 'errorreporting'],
    ('Management & Observability', 'Parameter Manager'): ['parametermanager'],

    # Networking
    ('Networking', 'Cloud CDN'): ['cdn'],
    ('Networking', 'Cloud DNS'): ['dns'],
    ('Networking', 'Cloud NAT'): ['cloud-nat'],
    ('Networking', 'Cloud Router'): ['cloud-router'],
    ('Networking', 'Cloud VPN'): ['vpn'],
    ('Networking', 'Connect Gateway'): ['connectgateway'],
    ('Networking', 'Media CDN'): ['media-cdn', 'mediacdn'],
    ('Networking', 'Network Connectivity Center'): ['network-connectivity'],
    ('Networking', 'Service Directory'): ['service-directory', 'servicedirectory'],
    ('Networking', 'Traffic Director'): ['traffic-director'],
    ('Networking', 'Virtual Private Cloud (VPC)'): ['vpc'],

    # Security and Identity
    ('Security and Identity', 'Access Approval'): ['accessapproval'],
    ('Security and Identity', 'Identity and Access Management (IAM)'): ['iam'],
    ('Security and Identity', 'Identity-Aware Proxy (IAP)'): ['iap'],
    ('Security and Identity', 'Key Management Service (KMS)'): ['kms'],
    ('Security and Identity', 'Private Certificate Authority'): ['privateca'],
    ('Security and Identity', 'reCAPTCHA Enterprise'): ['recaptcha'],
    ('Security and Identity', 'Secret Manager'): ['secret-manager', 'secretmanager'],
    ('Security and Identity', 'Security Command Center'): ['security-command-center', 'securitycenter'],
    ('Security and Identity', 'Web Risk'): ['webrisk'],
    ('Security and Identity', 'Web Security Scanner'): ['web-security-scanner'],

    # Storage
    ('Storage', 'Cloud Storage'): ['storage'],
    ('Storage', 'Filestore'): ['filestore'],
    ('Storage', 'Persistent Disk'): ['persistent-disk'],
    ('Storage', 'Storage Transfer Service'): ['storagetransfer'],

    # Hybrid and Multicloud
    ('Hybrid and Multicloud', 'Anthos'): ['anthos', 'servicemesh', 'gkeonaws'],

    # Other Services
    ('Other Services', 'Google Analytics Data API'): ['analyticsdata'],
    ('Other Services', 'Workflows'): ['workflows'],
}

# Ordered list to check for specific products before general ones.
ORDERED_PRODUCTS = [
    ('Data Analytics', 'BigQuery Migration'),
    ('Data Analytics', 'BigQuery Data Transfer'),
    ('Data Analytics', 'BigQuery Reservation'),
    ('Data Analytics', 'BigQuery Connection'),
    ('Databases', 'Cloud SQL'),
    ('Storage', 'Storage Transfer Service'),
    ('Storage', 'Storage Insights'),
    ('Storage', 'Storage Control'),
    ('AI and Machine Learning', 'Vertex AI Search'),
]
all_products = list(PRODUCT_HIERARCHY.keys())
for product in all_products:
    if product not in ORDERED_PRODUCTS:
        ORDERED_PRODUCTS.append(product)

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def _find_product_by_rules(search_string: str) -> tuple[str, str] or None:
    """Iterates through the ordered list of products to find the first keyword match."""
    if not isinstance(search_string, str):
        return None

    search_string_lower = search_string.lower()
    for category, product in ORDERED_PRODUCTS:
        keywords = PRODUCT_HIERARCHY.get((category, product), [])
        for keyword in keywords:
            try:
                if re.search(keyword, search_string_lower):
                    return category, product
            except re.error:
                if keyword in search_string_lower:
                    return category, product
    return None

def _categorize_with_llm(code_content: str, product_list: list) -> tuple[str, str]:
    """
    Placeholder for your LLM call. Analyzes code content to find the best product match.
    """
    # ---- REPLACE THIS SECTION WITH YOUR ACTUAL LLM CLIENT (e.g., Vertex AI) ----
    #
    # Example using Vertex AI Gemini:
    #
    # import vertexai
    # from vertexai.generative_models import GenerativeModel
    # import json
    #
    # vertexai.init(project="your-gcp-project-id", location="your-gcp-location")
    # model = GenerativeModel("gemini-1.5-flash-001")
    #
    # # Construct the prompt
    # formatted_product_list = "\n".join([f"- Category: {cat}, Product: {prod}" for cat, prod in product_list])
    #
    # prompt = f"""
    # You are an expert Google Cloud developer. Your task is to categorize a code sample into a specific Google Cloud product.
    # Analyze the following code, paying close attention to import statements, client library initializations, and API calls.
    #
    # Code Sample:
    # ```    # {code_content[:15000]}
    # ```
    #
    # Based on your analysis, choose the single best-fitting product from the following list:
    # {formatted_product_list}
    #
    # Return your answer as a single, valid JSON object with two keys: "category" and "product". Do not include any other text or formatting.
    # Example: {{"category": "Databases", "product": "Spanner"}}
    # """
    #
    # try:
    #     response = model.generate_content(prompt)
    #     result = json.loads(response.text)
    #     return result.get("category", "Uncategorized"), result.get("product", "Uncategorized")
    # except (json.JSONDecodeError, AttributeError, Exception) as e:
    #     print(f"LLM parsing failed: {e}")
    #     return "Uncategorized", "Uncategorized"
    #
    # ---- END OF REPLACEABLE SECTION ----

    # For demonstration purposes, this placeholder returns a default value.
    print("\n---> Rules-based categorization failed. Falling back to LLM analysis...")
    print("(This is a placeholder. Replace `_categorize_with_llm` with your actual LLM client.)")
    # Simulate a successful LLM call for a hypothetical case
    if "from google.cloud import bigquery" in code_content:
         return "Data Analytics", "BigQuery"
    return "Uncategorized", "Uncategorized"


# ==============================================================================
# 3. MAIN PUBLIC FUNCTION
# ==============================================================================

def categorize_sample(row_data: dict, code_content: str = "") -> tuple[str, str]:
    """
    Categorizes a single sample into a product category and product name.

    Args:
        row_data: A dictionary representing a row from the CSV, must contain keys:
                  'indexed_source_url', 'region_tag', 'repository_name'.
        code_content: The actual string content of the code file from the URL.
                      This is used as a fallback if rules-based methods fail.

    Returns:
        A tuple containing (product_category, product_name).
        Returns ('Uncategorized', 'Uncategorized') if no match is found.
    """
    # Stage 1: Attempt categorization using the fast, deterministic rules engine.
    # Priority Order: URL -> region_tag -> repository_name
    for field in ['indexed_source_url', 'region_tag', 'repository_name']:
        result = _find_product_by_rules(row_data.get(field))
        if result:
            return result

    # Stage 2: If no match, fall back to the LLM using the code content.
    if code_content:
        llm_result = _categorize_with_llm(code_content, ORDERED_PRODUCTS)
        if llm_result[0] != 'Uncategorized':
            return llm_result

    # If all methods fail, return Uncategorized.
    return 'Uncategorized', 'Uncategorized'


# ==============================================================================
# 4. EXAMPLE USAGE
# ==============================================================================

if __name__ == '__main__':
    # --- Example 1: Clear case, solvable by URL ---
    sample_row_1 = {
        'region_tag': 'spanner_quickstart',
        'repository_name': 'googleapis/java-spanner',
        'indexed_source_url': 'https://github.com/googleapis/java-spanner/samples/snippets/src/main/java/com/example/spanner/QuickstartSample.java'
    }
    print(f"Processing row 1: {sample_row_1['indexed_source_url']}")
    category, product = categorize_sample(sample_row_1)
    print(f"Result -> Category: '{category}', Product: '{product}'")
    print("-" * 30)


    # --- Example 2: Ambiguous URL, solvable by region_tag ---
    sample_row_2 = {
        'region_tag': 'mediacdn_sign_url',
        'repository_name': 'GoogleCloudPlatform/golang-samples',
        'indexed_source_url': 'https://github.com/GoogleCloudPlatform/golang-samples/mediacdn/sign_url.go'
    }
    print(f"Processing row 2: {sample_row_2['indexed_source_url']}")
    category, product = categorize_sample(sample_row_2)
    print(f"Result -> Category: '{category}', Product: '{product}'")
    print("-" * 30)


    # --- Example 3: Hypothetical case where rules fail, requiring LLM fallback ---
    sample_row_3 = {
        'region_tag': 'generic_sample_tag',
        'repository_name': 'generic-repo',
        'indexed_source_url': 'https://github.com/generic-repo/utils/main.py'
    }
    hypothetical_code_content = (
        "# A utility script for data processing\n"
        "from google.cloud import bigquery\n\n"
        "def run_query():\n"
        '    client = bigquery.Client(project="my-project")\n'
        '    query = """\n'
        '        SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013`\n'
        '    """\n'
        "    results = client.query(query)\n"
        "    for row in results:\n"
        "        print(row.name)\n"
    )
    print(f"Processing row 3 (hypothetical): {sample_row_3['indexed_source_url']}")
    category, product = categorize_sample(sample_row_3, code_content=hypothetical_code_content)
    print(f"Result -> Category: '{category}', Product: '{product}'")
    print("-" * 30)
