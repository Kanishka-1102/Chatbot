from model import handle_query

def test_model():
    # Sample queries to test the functionality
    queries = [
        "What are Ayurvedic remedies for cough?",
        "What precautions should I take when using Tulsi for cold?",
        "What are the benefits of Ashwagandha?",
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print("Response:")
        try:
            response = handle_query(query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    test_model()
