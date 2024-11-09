import streamlit as st

def display_ingredients(matched_ingredients, user_allergy):
    # Separate ingredients that match the user's allergy
    allergic_ingredients = [
        (ingredient, level, allergy, confidence)
        for ingredient, level, allergy, confidence in matched_ingredients
        if allergy == user_allergy and allergy != 0
    ]

    # Display allergic ingredients at the top in a warning color
    if allergic_ingredients:
        st.markdown("### ⚠️ Ingredients matching your allergy ⚠️")
        for ingredient, level, _, confidence in allergic_ingredients:
            color = get_level_color(level)  # Get color based on level
            st.markdown(
                f"<div style='background-color:{color}; padding:10px; border-radius:5px; text-align: center; color: black'>"
                f"<b>{ingredient}</b> (Confidence: {confidence:.2f})</div>"
                f"</br>",
                unsafe_allow_html=True,
            )

    # Display all other ingredients
    st.markdown("### All Ingredients")
    for ingredient, level, _, confidence in matched_ingredients:
        color = get_level_color(level)  # Get color based on level
        st.markdown(
            f"<div style='background-color:{color}; padding:10px; border-radius:5px; text-align: center; color: black'>"
            f"<b>{ingredient}</b> (Confidence: {confidence:.2f})</div>"
            f"</br>",
            unsafe_allow_html=True,
        )

def get_level_color(level):
    # Define colors based on levels with specific hex color codes
    if level == 3:
        return '#ff0909'  # Red for level 3
    elif level == 2:
        return '#ff9413'  # Orange for level 2
    elif level == 1:
        return '#f4db0b'  # Yellow for level 1
    else:
        return '#25ff0f'  # Green for level 0
