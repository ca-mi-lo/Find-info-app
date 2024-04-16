import streamlit as st

recipe  = {
    'rice': 3.0,
    'cheese': 5.0
}

temp_data_entered = 'x'  

ss = st.session_state

def changed_ingredient():
    if ss.recipe_memory_changed:
        # "acá sería  
        #if ss.recipe_memory[1] is in ss.recipe_memory_changed:
        if len(ss.recipe_memory_changed) > len(ss.recipe_memory[1]):
            ingredient = set(ss.recipe_memory_changed) - set(list(ss.recipe_memory[1].keys()))
            ingredient = list(ingredient)[0]
            ss.recipe_memory[1][ingredient] = 0.0

        elif len(ss.recipe_memory_changed) < len(ss.recipe_memory[1]):
            ingredient = set(list(ss.recipe_memory[1].keys())) - set(ss.recipe_memory_changed)
            ingredient = list(ingredient)[0]
            del ss.recipe_memory[1][ingredient]  # update recipe in memory


if "recipe_memory" not in ss:
    ss.recipe_memory = ["", recipe, temp_data_entered]


selected_ingredients = st.multiselect('Choose ingredients for your recipe',
                                      ['rice', 'cheese', 'apples', 'water'],
                                      on_change=changed_ingredient,
                                      default=list(ss.recipe_memory[1].keys()),
                                      key="recipe_memory_changed"
)

list(ss.recipe_memory[1].keys())


for key in list(ss.recipe_memory[1].keys()):
    ss.recipe_memory[1][key] = st.number_input(key, min_value=0., value=0.0)


#ss.recipe_memory[1][key]
ss.recipe_memory[1]
st.write(set(list(ss.recipe_memory[1].keys())))

