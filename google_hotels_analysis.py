# -*- coding: utf-8 -*-
"""google_hotels_analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1w-DM6P2H1qCLr2CoI5xu3cIAklL_6d2Y

# Analyzing Hotels on Google Search: The Impact of Ratings, Number of Reviews, Amenities, and Attractions

## 1. Data Extraction
"""

# @title Install and Import Libraries
# Install all libraries
!pip install pandas
!pip install numpy
!pip install matplotlib
!pip install seaborn
!pip install beautifulsoup4
!pip install requests
!pip install regex
!pip install googlemaps
!pip install geopy

print("All libraries installed")

# Import all libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import json
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps
from datetime import datetime
import os
from IPython.display import Image, display

print("All libraries imported")

# @title Gather Data
# Ask user for destination
destination = input("Enter your vacation destination (ex. Tokyo, Hawaii, etc.): ").strip().upper()
print(f"Let's optimize and visualize a 6-night hotel stay from December 22-28 in {destination}")

# Make 1st GET request for Relevant and Recommended Results
r_1 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqCwoHKAg6A0NBRBoA&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_1.status_code)

# Parse the HTML
soup = BeautifulSoup(r_1.content, 'html.parser')
print(soup.prettify())

# Find all hotel elements on the page
hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

# Extract hotel details (name, total rate, rating, number of reviews)
def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

# Extract details for each hotel and convert into a list
hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

# Save the results into a JSON file
with open('hotels_1.json', 'w') as f:
    json.dump(hotels, f, indent=4)

# Load the JSON file
with open('hotels_1.json', 'r') as f:
    hotels = json.load(f)

# Convert it to a dataframe
hotels_df_1 = pd.DataFrame(hotels)
hotels_df_1.head()

# Clean and remove "$" from "Total Rate" column
hotels_df_1['Total Rate'] = hotels_df_1['Total Rate'].str.split('total').str[0]
hotels_df_1['Total Rate'] = hotels_df_1['Total Rate'].str.replace(',', '', regex=False)
hotels_df_1['Total Rate'] = hotels_df_1['Total Rate'].str.replace('$', '', regex=False)

# Clean Reviews Column
hotels_df_1['Number of Reviews'] = hotels_df_1['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_1['Number of Reviews'] = hotels_df_1['Number of Reviews'].str.replace(',', '')

hotels_df_1['Amenities'] = hotels_df_1['Reviews'].str.extract(r'mention(.*)')
hotels_df_1['Amenities'] = hotels_df_1['Amenities'].str.strip()
hotels_df_1.drop(columns=['Reviews'], inplace=True)

hotels_df_1.head()

# Repeat process for 5 more URL links to increase # of rows
r_2 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqDgoKEgECKAM6A0NBRBoA&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_2.status_code)
soup = BeautifulSoup(r_2.content, 'html.parser')
print(soup.prettify())

hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

with open('hotels_2.json', 'w') as f:
    json.dump(hotels, f, indent=4)

with open('hotels_2.json', 'r') as f:
    hotels = json.load(f)

hotels_df_2 = pd.DataFrame(hotels)

hotels_df_2['Total Rate'] = hotels_df_2['Total Rate'].str.split('total').str[0]
hotels_df_2['Total Rate'] = hotels_df_2['Total Rate'].str.replace(',', '', regex=False)
hotels_df_2['Total Rate'] = hotels_df_2['Total Rate'].str.replace('$', '', regex=False)

hotels_df_2['Number of Reviews'] = hotels_df_2['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_2['Number of Reviews'] = hotels_df_2['Number of Reviews'].str.replace(',', '')

hotels_df_2['Amenities'] = hotels_df_2['Reviews'].str.extract(r'mention(.*)')
hotels_df_2['Amenities'] = hotels_df_2['Amenities'].str.strip()

hotels_df_2.drop(columns=['Reviews'], inplace=True)
hotels_df_2.head()

r_3 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqCwoHKA06A0NBRBoA&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_3.status_code)

soup = BeautifulSoup(r_3.content, 'html.parser')
print(soup.prettify())

hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

with open('hotels_3.json', 'w') as f:
    json.dump(hotels, f, indent=4)

with open('hotels_3.json', 'r') as f:
    hotels = json.load(f)

hotels_df_3 = pd.DataFrame(hotels)

hotels_df_3['Total Rate'] = hotels_df_3['Total Rate'].str.split('total').str[0]
hotels_df_3['Total Rate'] = hotels_df_3['Total Rate'].str.replace(',', '', regex=False)
hotels_df_3['Total Rate'] = hotels_df_3['Total Rate'].str.replace('$', '', regex=False)

hotels_df_3['Number of Reviews'] = hotels_df_3['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_3['Number of Reviews'] = hotels_df_3['Number of Reviews'].str.replace(',', '')

hotels_df_3['Amenities'] = hotels_df_3['Reviews'].str.extract(r'mention(.*)')
hotels_df_3['Amenities'] = hotels_df_3['Amenities'].str.strip()

hotels_df_3.drop(columns=['Reviews'], inplace=True)
hotels_df_3.head()

r_4 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqFAoJEgICAzoDQ0FEGgAiBRIDEJkB&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_4.status_code)

soup = BeautifulSoup(r_4.content, 'html.parser')
print(soup.prettify())

hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

with open('hotels_4.json', 'w') as f:
    json.dump(hotels, f, indent=4)

with open('hotels_4.json', 'r') as f:
    hotels = json.load(f)

hotels_df_4 = pd.DataFrame(hotels)

hotels_df_4['Total Rate'] = hotels_df_4['Total Rate'].str.split('total').str[0]
hotels_df_4['Total Rate'] = hotels_df_4['Total Rate'].str.replace(',', '', regex=False)
hotels_df_4['Total Rate'] = hotels_df_4['Total Rate'].str.replace('$', '', regex=False)

hotels_df_4['Number of Reviews'] = hotels_df_4['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_4['Number of Reviews'] = hotels_df_4['Number of Reviews'].str.replace(',', '')

hotels_df_4['Amenities'] = hotels_df_4['Reviews'].str.extract(r'mention(.*)')
hotels_df_4['Amenities'] = hotels_df_4['Amenities'].str.strip()

hotels_df_4.drop(columns=['Reviews'], inplace=True)
hotels_df_4.head()

r_5 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqFAoKEgECKAM6A0NBRBoAIgQSAhBu&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_5.status_code)

soup = BeautifulSoup(r_5.content, 'html.parser')
print(soup.prettify())

hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

with open('hotels_5.json', 'w') as f:
    json.dump(hotels, f, indent=4)

with open('hotels_5.json', 'r') as f:
    hotels = json.load(f)

hotels_df_5 = pd.DataFrame(hotels)

hotels_df_5['Total Rate'] = hotels_df_5['Total Rate'].str.split('total').str[0]
hotels_df_5['Total Rate'] = hotels_df_5['Total Rate'].str.replace(',', '', regex=False)
hotels_df_5['Total Rate'] = hotels_df_5['Total Rate'].str.replace('$', '', regex=False)

hotels_df_5['Number of Reviews'] = hotels_df_5['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_5['Number of Reviews'] = hotels_df_5['Number of Reviews'].str.replace(',', '')

hotels_df_5['Amenities'] = hotels_df_5['Reviews'].str.extract(r'mention(.*)')
hotels_df_5['Amenities'] = hotels_df_5['Amenities'].str.strip()

hotels_df_5.drop(columns=['Reviews'], inplace=True)
hotels_df_5.head()

r_6 = requests.get(f'https://www.google.com/travel/search?q={destination}&ts=CAESCgoCCAMKAggDEAAaNAoWEhIKCC9tLzAzZ2g0OgZIYXdhaWkaABIaEhQKBwjoDxAMGBYSBwjoDxAMGBwYBjICCAIqFAoJEgIEBToDQ0FEGgAiBQoDEPMH&ved=0CAAQ5JsGahgKEwiQ8on9m9-HAxUAAAAAHQAAAAAQngI&ictx=3&hl=en-CA&gl=ca&tcfs=Ei0KCC9tLzBkZmNuEgdP4oCYYWh1GhgKCjIwMjQtMTItMjISCjIwMjQtMTItMjgYAiIYCgoyMDI0LTA4LTExEgoyMDI0LTA4LTE3UgA&g2lb=4814050%2C4874190%2C4893075%2C4899571%2C4899573%2C4965990%2C4969803%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72421566%2C72462234%2C72470899%2C72471280%2C72472051%2C72473841%2C72481459%2C72485658%2C72486593%2C72494250%2C72499705%2C72520079%2C72536387%2C72549171%2C72569093%2C72570850%2C72602734%2C72616120%2C72619927%2C72620306%2C72634630%2C72639929%2C72639931%2C72647020%2C72648289%2C72653660%2C72658035%2C72662543%2C72662666%2C72670818%2C72671093%2C72672980&ap=MAE&qs=CAEgACgAOA1IAA')
print(r_6.status_code)

soup = BeautifulSoup(r_6.content, 'html.parser')
print(soup.prettify())

hotel_elements = soup.find_all('div', class_='uaTTDe BcKagd bLc2Te Xr6b1e')

def extract_hotel_details(hotel_element):

    hotel_name_element = hotel_element.find('h2', class_='BgYkof ogfYpf ykx2he')
    hotel_name = hotel_name_element.text.strip() if hotel_name_element else 'Not Found'

    total_rate_elements = hotel_element.find_all('div', class_='CQYfx UDzrdc')
    total_rates = [rate.text.strip() for rate in total_rate_elements if 'total' in rate.text]
    total_rates = total_rates if total_rates else ['Not Found']

    rating_element = hotel_element.find('span', class_='KFi5wf lA0BZ')
    rating = rating_element.text.strip() if rating_element else 'Not Found'

    reviews_element = hotel_element.find('span', class_='sSHqwe XLC8M')
    reviews = reviews_element.text.strip() if reviews_element else 'Not Found'

    return {
        'Hotel Name': hotel_name,
        'Total Rate': ', '.join(total_rates),
        'Rating': rating,
        'Reviews': reviews
    }

hotels = []
for hotel_element in hotel_elements:
    hotel_details = extract_hotel_details(hotel_element)
    hotels.append(hotel_details)

with open('hotels_6.json', 'w') as f:
    json.dump(hotels, f, indent=4)

with open('hotels_6.json', 'r') as f:
    hotels = json.load(f)

hotels_df_6 = pd.DataFrame(hotels)

hotels_df_6['Total Rate'] = hotels_df_6['Total Rate'].str.split('total').str[0]
hotels_df_6['Total Rate'] = hotels_df_6['Total Rate'].str.replace(',', '', regex=False)
hotels_df_6['Total Rate'] = hotels_df_6['Total Rate'].str.replace('$', '', regex=False)

hotels_df_6['Number of Reviews'] = hotels_df_6['Reviews'].str.extract(r'\((\d{1,3}(?:,\d{3})*)\)')
hotels_df_6['Number of Reviews'] = hotels_df_6['Number of Reviews'].str.replace(',', '')

hotels_df_6['Amenities'] = hotels_df_6['Reviews'].str.extract(r'mention(.*)')
hotels_df_6['Amenities'] = hotels_df_6['Amenities'].str.strip()

hotels_df_6.drop(columns=['Reviews'], inplace=True)
hotels_df_6.head()

"""## 2. Data Cleaning and Analysis"""

# Combine all the dataframes
combined_hotels = pd.concat([hotels_df_1, hotels_df_3, hotels_df_3, hotels_df_4, hotels_df_5, hotels_df_6], ignore_index=True)
combined_hotels = combined_hotels.drop_duplicates(subset='Hotel Name', keep='first')
combined_hotels.reset_index(drop=True, inplace=True)
combined_hotels.replace(['Not Found', '" '], np.nan, inplace=True)
combined_hotels.dropna(inplace=True)
combined_hotels = combined_hotels[combined_hotels['Amenities'].str.strip() != '']
combined_hotels.to_csv('combined_hotels.csv', index=False)

# Load the new joint dataframe
combined_hotels = pd.read_csv('combined_hotels.csv')
combined_hotels

# Split text based on uppercase letters and change 'Reviews' column spacing
def split_by_uppercase(text):
    return re.split(r'(?<!^)(?=[A-Z])', text.replace(' · ', ' ').strip())

# Apply function to split amenities by uppercase letters
combined_hotels['Amenities List'] = combined_hotels['Amenities'].apply(lambda x: split_by_uppercase(x))

# Explode the list into separate rows and create dummy variables
amenities_exploded = combined_hotels.explode('Amenities List')
amenities_dummies = pd.get_dummies(amenities_exploded['Amenities List'])
combined_hotels_dummies = amenities_dummies.groupby(amenities_exploded.index).max()

# Clean dummy variables and drop 'Amenities' and 'Amenities List' columns
# combined_hotels_dummies['TV'] = combined_hotels_dummies['T'] + combined_hotels_dummies['V']
combined_hotels_dummies['Wi-Fi'] = combined_hotels_dummies['Wi-'] + combined_hotels_dummies['Fi']
# combined_hotels_dummies.drop(columns=['T', 'V'], inplace=True)
combined_hotels_dummies.drop(columns=['Wi-'], inplace=True)
combined_hotels_dummies.drop(columns=['Fi'], inplace=True)
combined_hotels_dummies.drop(columns=['Fi '], inplace=True)
v_only_columns = [col for col in combined_hotels_dummies.columns if col.strip().upper() == 'V']
t_only_columns = [col for col in combined_hotels_dummies.columns if col.strip().upper() == 'T']
combined_hotels_dummies.drop(columns=v_only_columns, inplace=True)
combined_hotels_dummies.drop(columns=t_only_columns, inplace=True)
combined_hotels.drop(columns=['Amenities'], inplace=True)
combined_hotels.drop(columns=['Amenities List'], inplace=True)

# Merge the dummy columns with the combined_hotels dataframe
combined_hotels = combined_hotels.join(combined_hotels_dummies)
combined_hotels.head()

# Check for column duplicates
combined_hotels.columns = combined_hotels.columns.str.strip()
combined_hotels.columns

# Keep only the first column from the duplicates
combined_hotels = combined_hotels.loc[:, ~combined_hotels.columns.str.strip().duplicated(keep='first')]

# Check the remaining columns
combined_hotels.columns

"""## 3. Data Visualization"""

# Plot distribution of hotel ratings
sns.histplot(combined_hotels['Rating'], bins=10, kde=True)
plt.xlabel('Rating')
plt.ylabel('Number of Hotels')
plt.title('Distribution of Hotel Ratings')
plt.show()

# Plot the distribution of review count
sns.histplot(combined_hotels['Number of Reviews'], bins=20, kde=True)
plt.xlabel('Number of Reviews')
plt.ylabel('Frequency')
plt.title('Distribution of Number of Reviews')
plt.show()

# Identify Amenity Columns
amenities_plot = combined_hotels.columns[7:]
counts = combined_hotels[amenities_plot].sum().reset_index()
counts.columns = ['Amenities', 'Count']

# Plot the bar chart
plt.figure(figsize=(20, 6))
sns.barplot(x='Amenities', y='Count', data=counts, palette='flare_r')

# Add labels and titles
plt.xlabel('Amenities')
plt.ylabel('Number of Hotels')
plt.title('Count of Hotels with Each Amenity')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('amenities_count.png')
plt.show()

# Create a horizontal bar plot visualizing total rates for each hotel
bar_df = combined_hotels[['Hotel Name', 'Total Rate']].sort_values(by='Total Rate', ascending=False)
plt.figure(figsize=(12, 8))
sns.barplot(x='Total Rate', y='Hotel Name', data=bar_df, palette='viridis')

# Add labels and titles
plt.xlabel('Total Rate')
plt.ylabel('Hotel Name')
plt.title('Total Rates for Each Hotel')
plt.savefig('total_rates_per_hotel.png')
plt.show()

# Create a horizontal bar plot visualizing total rates for each hotel
bar_df = combined_hotels[['Hotel Name', 'Rating']].sort_values(by='Rating', ascending=False)
plt.figure(figsize=(12, 8))
sns.barplot(x='Rating', y='Hotel Name', data=bar_df, palette='crest')

# Add labels and titles
plt.xlabel('Rating')
plt.ylabel('Hotel Name')
plt.title('Ratings for Each Hotel')
plt.savefig('ratings_per_hotel.png')
plt.show()

# Prepare data
amenities = combined_hotels.columns[7:]
features = list(amenities) + ['Rating']
correlation_data = combined_hotels[features + ['Total Rate']].copy()

# Create a correlation matrix between Total Rate and Amenities + Rating
correlation_matrix = correlation_data.corr()

# Plot the heatmap
plt.figure(figsize=(14, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, annot_kws={"size": 10})
plt.title('Correlation Matrix between Total Rate and Amenities + Rating')
plt.show()

# Use the geopy library to obtain the address, latitude, and longitude for each hotel
def geocode_address(address, geolocator):
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.address, location.latitude, location.longitude
        else:
            return None, None, None
    except GeocoderTimedOut:
        return geocode_address(address, geolocator)

# Geocode each hotel name
geolocator = Nominatim(user_agent="hotel_geocoder")

addresses = []
latitudes = []
longitudes = []

for hotel_name in combined_hotels['Hotel Name']:
    formatted_address, lat, lng = geocode_address(hotel_name, geolocator)
    addresses.append(formatted_address)
    latitudes.append(lat)
    longitudes.append(lng)

combined_hotels['Address'] = addresses
combined_hotels['Latitude'] = latitudes
combined_hotels['Longitude'] = longitudes
combined_hotels.to_csv('geo_hotels.csv', index=False)

# Save and load results into a dataframe
geo_hotels = pd.read_csv('geo_hotels.csv')
geo_hotels.dropna(inplace=True)
geo_hotels.head()

# Use Google Maps "Places" or "GeoLocator" API to identify attractions and attraction distances from each hotel
gmaps = googlemaps.Client(key=your_api_key)

def find_nearest_attractions(address, gmaps, radius=1000, keyword='attraction'):
    try:
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return [], [], []

        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        places_result = gmaps.places_nearby((lat, lng), radius=radius, keyword=keyword)
        places = places_result.get('results', [])
        names = [place['name'] for place in places]
        addresses = [place['vicinity'] for place in places]
        distances = [gmaps.distance_matrix((lat, lng), place['geometry']['location'], mode='walking')['rows'][0]['elements'][0]['distance']['text'] for place in places]

        return names, addresses, distances
    except Exception as e:
        print(f"Error finding attractions: {e}")
        return [], [], []

attraction_names = []
attraction_addresses = []
attraction_distances = []

for address in geo_hotels['Address']:
    names, addresses, distances = find_nearest_attractions(address, gmaps)
    attraction_names.append(names)
    attraction_addresses.append(addresses)
    attraction_distances.append(distances)

# Load and save results into a dataframe
geo_hotels['Attractions'] = attraction_names
geo_hotels['Attraction Addresses'] = attraction_addresses
geo_hotels['Attraction Distances'] = attraction_distances
geo_hotels

# Plot the top 20 most frequently mentioned nearest attractions for each hotel
all_attractions = [attraction for sublist in geo_hotels['Attractions'] for attraction in sublist]

def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.split())
capitalized_attractions = [capitalize_words(attraction) for attraction in all_attractions]
unique_attractions = pd.Series(capitalized_attractions).drop_duplicates()
attraction_counts = pd.Series(capitalized_attractions).value_counts()

top_attractions = attraction_counts.head(20)
top_attractions_df = top_attractions.reset_index()
top_attractions_df.columns = ['Attraction', 'Number of Occurrences']

# Plot histogram
plt.figure(figsize=(12, 8))
sns.barplot(x='Number of Occurrences', y='Attraction', data=top_attractions_df, palette='crest')
plt.xlabel('Number of Occurrences')
plt.ylabel('Attraction')
plt.title('Top 20 Nearby Attractions')
plt.tight_layout()
plt.savefig('top_20_attractions.png')
plt.show()

# Create a scatter plot visualizing the relationship between rating and total rate, including the number of nearby attractions for each hotel (data point)
geo_hotels['Num_Attractions'] = geo_hotels['Attractions'].apply(len)
plt.figure(figsize=(12, 8))
scatter = sns.scatterplot(
    x='Rating',
    y='Total Rate',
    data=geo_hotels,
    hue='Num_Attractions',
    palette='crest',
    size='Num_Attractions',
    sizes=(20, 200),
    legend='full'
)
sns.regplot(
    x='Rating',
    y='Total Rate',
    data=geo_hotels,
    scatter=False,
    color='blue'
)

# Add labels and title
plt.xlabel('Rating')
plt.ylabel('Total Rate')
plt.title('Scatter Plot of Rating vs. Total Rate with Best Fit Line')

# Calculate and annotate the correlation coefficient
correlation = np.corrcoef(geo_hotels['Rating'], geo_hotels['Total Rate'])[0, 1]
plt.annotate(
    f'Correlation coefficient: {correlation:.2f}',
    xy=(0.05, 0.95),
    xycoords='axes fraction',
    fontsize=12,
    bbox=dict(boxstyle='round', facecolor='white', edgecolor='black')
)
handles, labels = scatter.get_legend_handles_labels()
plt.legend(
    handles=handles,
    title='Number of Attractions',
    bbox_to_anchor=(1.05, 1),
    loc='upper left'
)

plt.tight_layout()
plt.savefig('rating_vs_num_attractions.png')
plt.show()

