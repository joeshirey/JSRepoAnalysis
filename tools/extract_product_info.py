import re
import os
import yaml
import json
from collections import OrderedDict
from typing import Optional
from config import settings
from google import genai
from google.genai import types

# ==============================================================================
# 1. THE HIERARCHY AND KEYWORD MAPPING (LOADED FROM YAML)
# ==============================================================================

def _load_product_config():
    """Loads the product hierarchy and keywords from an external YAML file."""
    hierarchy = {}
    ordered_products = [
        # This list defines a specific priority order for matching.
        # Products here will be checked before any others.
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
    
    # Construct the full path to the YAML file relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, 'product_hierarchy.yaml')

    with open(yaml_path, 'r') as f:
        product_config = yaml.safe_load(f)

    all_products_from_yaml = []
    for category_info in product_config:
        category_name = category_info['category']
        for product_info in category_info['products']:
            product_name = product_info['product']
            key = (category_name, product_name)
            hierarchy[key] = product_info.get('keywords', [])
            all_products_from_yaml.append(key)

    # Add the remaining products from YAML, ensuring no duplicates and preserving priority
    for product in all_products_from_yaml:
        if product not in ordered_products:
            ordered_products.append(product)
            
    return hierarchy, ordered_products

# Load the configuration once when the module is imported
PRODUCT_HIERARCHY, ORDERED_PRODUCTS = _load_product_config()


# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def _find_product_by_rules(search_string: str) -> Optional[tuple[str, str]]:
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
    Analyzes code content using an LLM to find the best product match.
    """
    print("\n---> Rules-based categorization failed. Falling back to LLM analysis...")
    
    try:
        # Initialize the genai client
        client = genai.Client()

        # Construct the prompt
        formatted_product_list = "\n".join([f"- Category: {cat}, Product: {prod}" for cat, prod in product_list])
        
        prompt = f"""
        You are an expert Google Cloud developer. Your task is to categorize a code sample into a specific Google Cloud product.
        Analyze the following code, paying close attention to import statements, client library initializations, and API calls.

        Code Sample:
        ```
        {code_content[:15000]}
        ```

        Based on your analysis, choose the single best-fitting product from the following list:
        {formatted_product_list}

        Return your answer as a single, valid JSON object with two keys: "category" and "product". Do not include any other text or formatting.
        Example: {{\"category\": \"Databases\", \"product\": \"Spanner\"}}
        """

        # Configure generation parameters
        generation_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
        )

        response = client.models.generate_content(
            model=settings.VERTEXAI_MODEL_NAME,
            contents=prompt,
            config=generation_config,
        )
        
        # Clean up the response text to ensure it's valid JSON
        text_to_load = response.text.strip()
        match = re.search(r'```json\s*({.*?})\s*```', text_to_load, re.DOTALL)
        if match:
            text_to_load = match.group(1)

        result = json.loads(text_to_load)
        category = result.get("category", "Uncategorized")
        product = result.get("product", "Uncategorized")
        
        print(f"---> LLM categorized as: Category='{category}', Product='{product}'")
        return category, product

    except (json.JSONDecodeError, AttributeError, Exception) as e:
        print(f"LLM categorization or parsing failed: {e}")
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
