# Deliberately mixed quality questions
# Some good, some bad — so Arize has failures to detect

QUESTIONS = [
    # ✅ Normal valid questions
    "What is your return policy?",
    "How do I track my order?",
    "What payment methods do you accept?",
    "How long does shipping take?",
    "Can I cancel my order?",

    # ❌ Gibberish inputs
    "asdfjkl qwerty???",
    "123 456 !!!###",

    # ❌ Out of scope
    "What is the meaning of life?",
    "Do you ship to Mars?",
    "Can you help me with my taxes?",

    # ❌ Aggressive / vague
    "REFUND NOW!!!",
    "Why is your service so bad?",
    "This is terrible, fix it!!!",

    # ❌ Contradictory / impossible
    "I want a refund for something I never bought",
    "Can I return an item I bought 5 years ago?",
]