import json
import math
import re
from collections import Counter
from pathlib import Path

import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
PROJECT_DIR = Path(__file__).parent
FOOD_INFO_PATH = PROJECT_DIR / "food_info.json"
DEFAULT_FOOD_IMAGE = PROJECT_DIR / "assets" / "images" / "default-food.svg"

UI_TEXT = {
    "English": {
        "language": "Language",
        "page_title": "RAG FoodBot",
        "title": "RAG Food Recommendation Chatbot",
        "caption": "Ask by mood, cuisine, diet, budget, spice level, or meal time.",
        "info": "Corrected app: local-only RAG from the data folder. No Gemini, Google API, or paid AI API calls are used.",
        "knowledge_base": "Knowledge Base",
        "knowledge_base_description": "This chatbot retrieves from local text files in the data folder before answering.",
        "documents": "Documents",
        "try_asking": "Try asking",
        "chat_placeholder": "Example: spicy Indian food under Rs. 200",
        "retrieved_context": "Retrieved context",
        "no_context": "No matching data file was retrieved.",
        "calories": "Calories",
        "calories_unavailable": "Not available",
    },
    "Telugu": {
        "language": "భాష",
        "page_title": "RAG ఫుడ్‌బాట్",
        "title": "RAG ఆహార సిఫార్సు చాట్‌బాట్",
        "caption": "మీ మూడ్, వంటకం, ఆహార అభిరుచి, బడ్జెట్, కారపు స్థాయి లేదా భోజన సమయాన్ని అడగండి.",
        "info": "ఈ యాప్ డేటా ఫోల్డర్‌లోని స్థానిక ఫైళ్లను మాత్రమే ఉపయోగిస్తుంది. Gemini, Google API లేదా చెల్లింపు AI APIలను ఉపయోగించదు.",
        "knowledge_base": "జ్ఞాన భాండారం",
        "knowledge_base_description": "ఈ చాట్‌బాట్ సమాధానం ఇవ్వడానికి ముందు డేటా ఫోల్డర్‌లోని స్థానిక టెక్స్ట్ ఫైళ్ల నుండి సమాచారాన్ని పొందుతుంది.",
        "documents": "పత్రాలు",
        "try_asking": "ఇలా అడగండి",
        "chat_placeholder": "ఉదాహరణ: రూ. 200 లోపు కారంగా ఉండే భారతీయ ఆహారం",
        "retrieved_context": "పొందిన సమాచారం",
        "no_context": "సరిపోలే డేటా ఫైల్ కనుగొనబడలేదు.",
        "calories": "కేలరీలు",
        "calories_unavailable": "అందుబాటులో లేదు",
    },
    "Hindi": {
        "language": "भाषा",
        "page_title": "RAG फ़ूडबॉट",
        "title": "RAG भोजन सुझाव चैटबॉट",
        "caption": "मूड, व्यंजन, आहार, बजट, मसाले के स्तर या भोजन के समय के आधार पर पूछें।",
        "info": "यह ऐप डेटा फ़ोल्डर की स्थानीय फ़ाइलों का उपयोग करता है। इसमें Gemini, Google API या सशुल्क AI API का उपयोग नहीं होता।",
        "knowledge_base": "ज्ञान आधार",
        "knowledge_base_description": "यह चैटबॉट जवाब देने से पहले डेटा फ़ोल्डर की स्थानीय टेक्स्ट फ़ाइलों से जानकारी प्राप्त करता है।",
        "documents": "दस्तावेज़",
        "try_asking": "पूछकर देखें",
        "chat_placeholder": "उदाहरण: रु. 200 से कम में मसालेदार भारतीय खाना",
        "retrieved_context": "प्राप्त संदर्भ",
        "no_context": "कोई मेल खाती डेटा फ़ाइल नहीं मिली।",
        "calories": "कैलोरी",
        "calories_unavailable": "उपलब्ध नहीं",
    },
    "Tamil": {
        "language": "மொழி",
        "page_title": "RAG ஃபுட்பாட்",
        "title": "RAG உணவுப் பரிந்துரை சாட்பாட்",
        "caption": "மனம், உணவு வகை, உணவுப் பழக்கம், பட்ஜெட், கார அளவு அல்லது உணவு நேரம் பற்றி கேளுங்கள்.",
        "info": "இந்த செயலி தரவு கோப்புறையிலுள்ள உள்ளூர் கோப்புகளை மட்டுமே பயன்படுத்துகிறது. Gemini, Google API அல்லது கட்டண AI API பயன்படுத்தப்படவில்லை.",
        "knowledge_base": "அறிவுத் தளம்",
        "knowledge_base_description": "இந்த சாட்பாட் பதிலளிக்கும் முன் தரவு கோப்புறையிலுள்ள உள்ளூர் உரைக் கோப்புகளில் இருந்து தகவலைப் பெறுகிறது.",
        "documents": "ஆவணங்கள்",
        "try_asking": "கேட்டுப் பாருங்கள்",
        "chat_placeholder": "உதாரணம்: ரூ. 200-க்குள் காரமான இந்திய உணவு",
        "retrieved_context": "பெறப்பட்ட சூழல்",
        "no_context": "பொருந்தும் தரவுக் கோப்பு கிடைக்கவில்லை.",
        "calories": "கலோரிகள்",
        "calories_unavailable": "கிடைக்கவில்லை",
    },
    "Kannada": {
        "language": "ಭಾಷೆ",
        "page_title": "RAG ಫುಡ್‌ಬಾಟ್",
        "title": "RAG ಆಹಾರ ಶಿಫಾರಸು ಚಾಟ್‌ಬಾಟ್",
        "caption": "ಮನಸ್ಥಿತಿ, ಪಾಕಶೈಲಿ, ಆಹಾರ ಪದ್ಧತಿ, ಬಜೆಟ್, ಖಾರದ ಮಟ್ಟ ಅಥವಾ ಊಟದ ಸಮಯದ ಬಗ್ಗೆ ಕೇಳಿ.",
        "info": "ಈ ಅಪ್ಲಿಕೇಶನ್ ಡೇಟಾ ಫೋಲ್ಡರ್‌ನಲ್ಲಿರುವ ಸ್ಥಳೀಯ ಫೈಲ್‌ಗಳನ್ನು ಮಾತ್ರ ಬಳಸುತ್ತದೆ. Gemini, Google API ಅಥವಾ ಪಾವತಿಸಿದ AI APIಗಳನ್ನು ಬಳಸುವುದಿಲ್ಲ.",
        "knowledge_base": "ಜ್ಞಾನ ಭಂಡಾರ",
        "knowledge_base_description": "ಈ ಚಾಟ್‌ಬಾಟ್ ಉತ್ತರಿಸುವ ಮೊದಲು ಡೇಟಾ ಫೋಲ್ಡರ್‌ನಲ್ಲಿರುವ ಸ್ಥಳೀಯ ಪಠ್ಯ ಫೈಲ್‌ಗಳಿಂದ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯುತ್ತದೆ.",
        "documents": "ದಾಖಲೆಗಳು",
        "try_asking": "ಹೀಗೆ ಕೇಳಿ",
        "chat_placeholder": "ಉದಾಹರಣೆ: ರೂ. 200 ಒಳಗೆ ಖಾರವಾದ ಭಾರತೀಯ ಆಹಾರ",
        "retrieved_context": "ಪಡೆದ ಮಾಹಿತಿ",
        "no_context": "ಹೊಂದುವ ಡೇಟಾ ಫೈಲ್ ದೊರೆಯಲಿಲ್ಲ.",
        "calories": "ಕ್ಯಾಲೊರಿಗಳು",
        "calories_unavailable": "ಲಭ್ಯವಿಲ್ಲ",
    },
}


def get_ui_text():
    """Return the UI labels for the language selected in the sidebar."""
    language = st.session_state.get("language", "English")
    return UI_TEXT[language]


@st.cache_data
def load_food_info():
    """Load display-only food metadata without affecting recommendation logic."""
    if not FOOD_INFO_PATH.exists():
        return {}

    try:
        return json.loads(FOOD_INFO_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def get_food_image(food_info):
    """Use a food image when present, otherwise return the local fallback image."""
    image_path = PROJECT_DIR / food_info.get("image", "")
    return image_path if image_path.is_file() else DEFAULT_FOOD_IMAGE


def extract_recommended_foods(answer):
    """Read food names from the already-generated response for display cards."""
    section = answer.partition("Recommended foods:\n")[2].partition("\n\n")[0]
    return [line.removeprefix("- ") for line in section.splitlines() if line.startswith("- ")]


def display_food_details(food_names, ui):
    """Render calorie and rating details for the foods already recommended."""
    food_info = load_food_info()

    for index, food_name in enumerate(food_names):
        details = food_info.get(food_name, {})
        calories = details.get("calories", ui["calories_unavailable"])
        calorie_text = (
            f"{calories} kcal"
            if isinstance(calories, (int, float))
            else calories
        )

        rating_value = details.get("rating")
        if rating_value in (None, ""):
            rating_text = "4.5/5"
        elif isinstance(rating_value, (int, float)):
            rating_text = f"{float(rating_value):.1f}/5"
        else:
            rating_text = f"{rating_value}/5"

        st.markdown(f"**{food_name}**")
        st.write(f"🔥 {ui['calories']}: {calorie_text}")
        st.write(f"⭐ Rating: {rating_text}")
        if index < len(food_names) - 1:
            st.write("")

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
        "Recommended foods:\n\n"
    )
    answer += "\n".join(f"- {item}" for item in recommendations)
    answer += (
        f"\n\nMy best pick: {recommendations[0]}, because it closely matches your craving and preference."
    )
    return answer


def answer_user(query):
    contexts = retrieve_context(query)
    return build_answer(query, contexts), contexts


st.set_page_config(
    page_title=get_ui_text()["page_title"],
    page_icon="Food",
    layout="centered",
)

with st.sidebar:
    st.selectbox(
        get_ui_text()["language"],
        options=list(UI_TEXT),
        key="language",
    )

ui = get_ui_text()

st.title(ui["title"])
st.caption(ui["caption"])
st.info(ui["info"])

with st.sidebar:
    st.header(ui["knowledge_base"])
    st.write(ui["knowledge_base_description"])
    st.write(f"{ui['documents']}: {len(load_knowledge_base())}")
    st.divider()
    st.subheader(ui["try_asking"])
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
        if message["role"] == "assistant" and message.get("food_names"):
            display_food_details(message["food_names"], ui)

prompt = st.chat_input(ui["chat_placeholder"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response, retrieved_contexts = answer_user(prompt)
    recommended_foods = extract_recommended_foods(response)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "food_names": recommended_foods,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)
        display_food_details(recommended_foods, ui)
