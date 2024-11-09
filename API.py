from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image
from io import BytesIO
from OCR import perform_ocr
from Ingredients_Match import Match_Ingredient
from Output_Generator import display_ingredients
from Preprocess import img_preprocess, text_preprocess

# Initialize FastAPI app
app = FastAPI()

# API route for image processing and response generation
@app.post("/process-image/", response_class=HTMLResponse)
async def process_image(image: UploadFile = File(...), allergy: str = "None"):
    try:
        # Save the uploaded image
        img = Image.open(BytesIO(await image.read()))
        
        # Perform OCR on the image
        tokens = perform_ocr(img)
        
        # Match ingredients with tokens
        matched_ingredients = Match_Ingredient(tokens)
        
        # Map allergy to number
        allergy_map = {
            'None': 0,
            'Nut': 1,
            'Lactose': 2,
            'Wheat': 3,
            'Soy': 4,
            'Digestive/Skin': 5
        }
        allergy_number = allergy_map.get(allergy, 0)
        
        # Generate the HTML output for ingredients and allergy display
        html_output = display_ingredients(matched_ingredients, user_allergy=allergy_number)
        
        # Return the HTML content
        return HTMLResponse(content=html_output)
    
    except:
        return HTMLResponse(content="<h1>Something Want Wrong!</h1>", status_code=200)
# Root endpoint to check API status
@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse(content="<h1>NutriScanAI API is working!</h1>", status_code=200)
