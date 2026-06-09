from query import ask

TEST_QUERIES = [
    "What do students say about Saty Raghavachary's teaching style?",
    "What concerns were raised about CSCI 571?",
    "How do students compare CSCI 526 and CSCI 538?",
    "What is the best restaurant near USC?",
]

print("\n" + "="*60)
print("End-to-end generation test")
print("="*60 + "\n")

for i, query in enumerate(TEST_QUERIES, 1):
    print(f"Query {i}: {query}")
    print("─"*54)
    result = ask(query)
    print(f"Answer:\n{result['answer']}")
    print(f"\nSources: {', '.join(result['sources'])}")
    print("\n" + "="*60 + "\n")
