# RAG Food Recommendation Chatbot

This is a Streamlit chatbot for food recommendations. It uses text files in the `data/` folder as a local knowledge base and retrieves the most relevant food documents before creating an answer.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Example Questions

- I want something spicy under Rs. 200
- Suggest healthy vegetarian lunch
- I am sad and want comfort food
- Recommend non-veg Chinese food

## Data

The RAG knowledge base is stored in `.txt` files inside `data/`. Add more `.txt` files using this format:

```text
Title: Example Food Category
Write useful recommendation information here.
Items: Food item one, Food item two, Food item three
```
