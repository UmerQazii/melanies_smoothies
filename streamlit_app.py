# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on smoothie will be:", name_on_order)

# Ensure the connection and session are correctly configured
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Display dataframes for debugging
st.dataframe(pd_df, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + " Nutrition Information")
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        st.write(fruityvice_response.json())  # Display raw JSON for debugging

    st.write(ingredients_string)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                            VALUES (%s, %s)"""
        session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
        
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
