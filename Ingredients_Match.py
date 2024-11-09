import faiss
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the FAISS index, ingredient data, and model
index = faiss.read_index("Model/Faiss_Index.idx")  # Load FAISS index
ingredients = pd.read_pickle("Model/Ingredients_Embedding.pkl")  # Load ingredient data with original names, levels, and allergy info
model = pickle.load(open("Model/Ingredient_Model.pkl", "rb"))  # Load SentenceTransformer model

def Match_Ingredient(input_tokens, threshold=0.9):
    # Generate embeddings for the input tokens
    input_embeddings = model.encode(input_tokens, convert_to_tensor=True).cpu().numpy()
    faiss.normalize_L2(input_embeddings)  # Normalize for cosine similarity

    # Perform similarity search for each input token in FAISS
    k = 1  # Retrieve the closest match
    D, I = index.search(input_embeddings, k)

    # Define a confidence threshold and dictionary to store highest confidence matches
    matched_ingredients = {}

    for idx, token in enumerate(input_tokens):
        max_sim_value = D[idx][0]
        max_sim_idx = I[idx][0]

        # Check if the similarity score is above the threshold
        if max_sim_value >= threshold:
            matched_ingredient = ingredients.iloc[max_sim_idx]  # Access row by index

            # Extract values from matched ingredient row
            ingredient_name = matched_ingredient['Ingredient Name']  # Original ingredient name
            level = matched_ingredient['Level']
            allergy = matched_ingredient['Allergy']

            # Only add or replace if this match has higher confidence than any previous match for the same ingredient
            if ingredient_name not in matched_ingredients or matched_ingredients[ingredient_name][1] < max_sim_value:
                matched_ingredients[ingredient_name] = ((ingredient_name, level, allergy), max_sim_value)

    # Return a list of tuples with the original ingredient name, level, allergy, and confidence
    return [(ingredient[0], ingredient[1], ingredient[2], confidence)
            for ingredient, confidence in matched_ingredients.values()]
