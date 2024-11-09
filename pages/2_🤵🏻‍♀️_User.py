import streamlit as st
from PIL import Image
from datetime import date
from Database import insert_data
from streamlit_app import url, db, user_collection
from OCR import perform_ocr
from Ingredients_Match import Match_Ingredient
from Output_Generator import display_ingredients

st.markdown("<h1 style='text-align: center; font-weight: bold;'>NutriScanAI</h1>", unsafe_allow_html=True)

allergy_map = {
    'None': 0,
    'Nut': 1,
    'Lactose': 2,
    'Wheat': 3,
    'Soy': 4,
    'Digestive/Skin': 5
}

Name = st.text_input("Enter Your Name:", max_chars=20)
Gender = st.radio("Select Your Gender:", options=["Male", "Female"], horizontal=True)
State = st.text_input("Enter Your State:", value="None")
Allergy = st.selectbox(label='If you Have Any Allergy:', options=['None', 'Nut', 'Lactose', 'Wheat', 'Soy', 'Digestive/Skin'])
Allergy_Number = allergy_map.get(Allergy, 0)
Date = str(date.today())


IngriSacn, NutriScan = st.tabs(['IngriSacn', 'NutriScan'])

with IngriSacn:
    st.header('IngriScan')
    st.write("Choose an Option:")
    Upload, Camera = st.tabs(['Upload File', 'Use Camera'])

    with Upload:
        uploded_image = st.file_uploader("Upload an Image File:", type=["jpg", "png", "jpeg"])
        if uploded_image is not None:
            try:
                image = Image.open(uploded_image)
                tokens = perform_ocr(image)
                matched_ingredients = Match_Ingredient(tokens)
                display_ingredients(matched_ingredients, user_allergy=Allergy_Number)
                st.markdown("""
                ### Ingredient Levels:
                - 🟥 **Level 3**: Red (Highest risk)
                - 🟧 **Level 2**: Orange
                - 🟨 **Level 1**: Yellow
                - 🟩 **Level 0**: Green (Lowest risk)
                """)
            except Exception as e:
                st.error(f"Error: {e}")

    with Camera:
        camera_image = st.camera_input("Use Camera for Input:")
        if camera_image is not None:
            try:
                image = Image.open(camera_image)
                tokens = perform_ocr(image)
                matched_ingredients = Match_Ingredient(tokens)
                display_ingredients(matched_ingredients, user_allergy=Allergy)
                st.markdown("""
                ### Ingredient Levels:
                - 🟥 **Level 3**: Red (Highest risk)
                - 🟧 **Level 2**: Orange
                - 🟨 **Level 1**: Yellow
                - 🟩 **Level 0**: Green (Lowest risk)
                """)
            except Exception as e:
                st.error(f"Error: {e}")

with NutriScan:
    st.header('NutriScan')
