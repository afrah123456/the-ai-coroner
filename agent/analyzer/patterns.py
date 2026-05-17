FAILURE_PATTERNS = [
    {
        "name": "Gibberish Input",
        "keywords": [
            "doesn't make sense",
            "not able to understand",
            "i'm not able to",
            "unclear",
            "i cannot understand",
            "i'm not sure what",
            "seems like random",
        ],
        "description": "User sent meaningless or random characters",
        "fix": "Add an input validation layer that detects and rejects gibberish before it reaches the LLM. Respond with: 'I didn't understand that — could you rephrase?'",
    },
    {
        "name": "Out of Scope",
        "keywords": [
            "not a tax",
            "philosophical",
            "outside",
            "not something i can",
            "i'm not able to help with that",
            "unfortunately",
            "beyond my role",
            "not within",
            "i'm afraid",
        ],
        "description": "User asked something completely unrelated to the app's purpose",
        "fix": "Improve the system prompt to explicitly list what topics are in and out of scope. Add a polite redirect message for out-of-scope questions.",
    },
    {
        "name": "Aggressive Input",
        "keywords": [
            "i'm sorry to hear",
            "i understand your frustration",
            "i apologize",
            "i'm here to help",
            "i can see you're",
            "i'm sorry you feel",
        ],
        "description": "User sent aggressive or emotionally charged messages",
        "fix": "Add a tone detection layer. For aggressive inputs, route to a specialized de-escalation prompt before attempting to resolve the issue.",
    },
    {
        "name": "Impossible Request",
        "keywords": [
            "5 years",
            "never bought",
            "mars",
            "we do not currently ship",
            "cannot process",
            "not possible",
        ],
        "description": "User made an impossible or contradictory request",
        "fix": "Train the model with more examples of impossible requests. Add clear policy statements to the system prompt about limitations.",
    },
    {
        "name": "Hallucination Risk",
        "keywords": [
            "i believe",
            "i think",
            "i'm not entirely sure",
            "it's possible that",
            "you might want to verify",
            "i'm not certain",
            "as far as i know",
        ],
        "description": "Bot expressed uncertainty or gave potentially hallucinated information",
        "fix": "Add a confidence scoring layer. When the model is uncertain, route to a fallback response or human escalation instead of guessing.",
    },
    {
        "name": "Toxic Output Risk",
        "keywords": [
            "i cannot assist with",
            "inappropriate",
            "i'm not able to engage",
            "offensive",
            "violates",
            "against our policy",
        ],
        "description": "Input triggered potentially harmful or policy-violating content",
        "fix": "Add a content moderation layer before and after LLM responses. Use a classifier to detect and block toxic inputs early.",
    },
    {
        "name": "Missing Information",
        "keywords": [
            "could you please provide",
            "i need more information",
            "can you clarify",
            "please provide your order",
            "i'd need your",
            "to assist you better",
        ],
        "description": "Bot couldn't help because user didn't provide enough context",
        "fix": "Add a guided input flow that collects required information upfront before routing to the LLM.",
    },
]


def classify_failure(output: str) -> dict:
    """Match a failure output to the most likely pattern."""
    output_lower = output.lower()

    for pattern in FAILURE_PATTERNS:
        if any(kw in output_lower for kw in pattern["keywords"]):
            return pattern

    return {
        "name": "Unknown Failure",
        "description": "Could not classify this failure pattern",
        "fix": "Manual review recommended — add this pattern to the classifier.",
    }