import math
import re
from collections import Counter
from pathlib import Path

import streamlit as st


DATA_DIR = Path(__file__).parent / "data"

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "based",
    "be",
    "for",
    "food",
    "i",
    "in",
    "is",
    "me",
    "of",
    "on",
    "or",
    "please",
    "suggest",
    "the",
    "to",
    "under",
    "want",
    "with",
}


def parse_items(content):
    match = re.search(r"Items:\s*(.+)", content, re.IGNORECASE)
    if not match:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


@st.cache_data
def load_knowledge_base():
    documents = []

    if not DATA_DIR.exists():
        return documents

    for path in sorted(DATA_DIR.glob("*.txt")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        title = path.stem.replace("_", " ").title()
        first_line, _, rest = content.partition("\n")

        if first_line.lower().startswith("title:"):
            title = first_line.split(":", 1)[1].strip()
            content = rest.strip()

        documents.append(
            {
                "title": title,
                "content": content,
                "items": parse_items(content),
                "source": path.name,
            }
        )

    return documents


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def cosine_similarity(query_tokens, document_tokens):
    query_counts = Counter(query_tokens)
    document_counts = Counter(document_tokens)
    shared_words = set(query_counts) & set(document_counts)

    numerator = sum(query_counts[word] * document_counts[word] for word in shared_words)
    query_norm = math.sqrt(sum(value * value for value in query_counts.values()))
    document_norm = math.sqrt(sum(value * value for value in document_counts.values()))

    if query_norm == 0 or document_norm == 0:
        return 0
    return numerator / (query_norm * document_norm)


def retrieve_context(query, top_k=3):
    query_tokens = tokenize(query)
    scored_docs = []

    for doc in load_knowledge_base():
        document_text = f"{doc['title']} {doc['content']} {' '.join(doc['items'])}"
        score = cosine_similarity(query_tokens, tokenize(document_text))
        scored_docs.append({**doc, "score": score})

    scored_docs.sort(key=lambda doc: doc["score"], reverse=True)
    return [doc for doc in scored_docs[:top_k] if doc["score"] > 0]


def extract_budget(query):
    normalized_query = query.lower().replace("₹", "rs")
    match = re.search(
        r"(?:under|below|less than|rs|rs\.|inr)\s*(\d{2,4})|(\d{2,4})\s*(?:rs|rs\.|inr)",
        normalized_query,
    )
    if not match:
        return None
    return match.group(1) or match.group(2)


def build_answer(query, contexts):
    budget = extract_budget(query)

    if not contexts:
        return (
            "I need one more detail to recommend well. Tell me your mood, cuisine, diet "
            "preference, or budget. Example: spicy under Rs. 200, healthy lunch, veg Indian, "
            "or sweet dessert."
        )

    recommendations = []
    for context in contexts:
        for item in context["items"]:
            if item not in recommendations:
                recommendations.append(item)

    recommendations = recommendations[:5]
    if not recommendations:
        return (
            "I found relevant food notes, but no recommendation items were listed in the "
            "retrieved data files. Please add an 'Items:' line to the matching data file."
        )

    context_titles = ", ".join(context["title"] for context in contexts)
    budget_line = f" I also noticed your budget is around Rs. {budget}." if budget else ""

    answer = (
        f"Based on your message, I retrieved: {context_titles}.{budget_line}\n\n"
        "Recommended foods:\n"
    )
    answer += "\n".join(f"- {item}" for item in recommendations)
    answer += (
        "\n\nMy best pick: "
        f"{recommendations[0]}, because it closely matches your craving and preference.\n\n"
        "Want me to filter this by veg/non-veg, cuisine, meal time, or nearby restaurants?"
    )
    return answer


def answer_user(query):
    contexts = retrieve_context(query)
    return build_answer(query, contexts), contexts


st.set_page_config(page_title="RAG FoodBot", page_icon="Food", layout="centered")

st.title("RAG Food Recommendation Chatbot")
st.caption("Ask by mood, cuisine, diet, budget, spice level, or meal time.")
st.info("Corrected app: local-only RAG from the data folder. No Gemini, Google API, or paid AI API calls are used.")

with st.sidebar:
    st.header("Knowledge Base")
    st.write("This chatbot retrieves from local text files in the data folder before answering.")
    st.write(f"Documents: {len(load_knowledge_base())}")
    st.divider()
    st.subheader("Try asking")
    st.code("I want something spicy under Rs. 200")
    st.code("Suggest healthy vegetarian lunch")
    st.code("I am sad and want comfort food")
    st.code("Recommend non-veg Chinese food")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I am FoodBot. Tell me what you feel like eating, your budget, "
                "or your cuisine preference."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Example: spicy Indian food under Rs. 200")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response, retrieved_contexts = answer_user(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

        with st.expander("Retrieved context"):
            if not retrieved_contexts:
                st.write("No matching data file was retrieved.")
            for context in retrieved_contexts:
                st.markdown(
                    f"**{context['title']}** - score `{context['score']:.2f}` - `{context['source']}`"
                )
                st.write(context["content"])
