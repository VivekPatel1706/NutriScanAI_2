import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# Load dataset
df = pd.read_csv('Data/CSV/Dataset.csv')

# Preprocess dataset ingredient names: remove spaces and make lowercase
df['Ingredient_cleaned'] = df['Ingredient Name'].str.replace(' ', '').str.lower()

# Load the sentence transformer model for embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for the cleaned ingredients in the dataset
ingredient_embeddings = model.encode(df['Ingredient_cleaned'].tolist(), convert_to_tensor=True).cpu().numpy()

# Initialize FAISS index for cosine similarity search
d = ingredient_embeddings.shape[1]
index = faiss.IndexFlatIP(d)
faiss.normalize_L2(ingredient_embeddings)  # Normalize to use cosine similarity
index.add(ingredient_embeddings)

# Save the FAISS index
faiss.write_index(index, "Model/Faiss_Index.idx")
print("FAISS Index is Saved!")

# Save the dataset with the original and cleaned ingredient names, level, and allergy data
df[['Ingredient Name', 'Ingredient_cleaned', 'Level', 'Allergy']].to_pickle("Model/Ingredients_Embedding.pkl")
print("Dataset and Embeddings are Saved!")

# Save the SentenceTransformer model
pickle.dump(model, open("Model/Ingredient_Model.pkl", "wb"))
print("SentenceTransformer Model is Saved!")
