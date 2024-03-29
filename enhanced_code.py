

from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st
import numpy as np

# Function to extract Product Title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id":'productTitle'})
        title_value = title.text
        title_string = title_value.strip()
    except AttributeError:
        title_string = ""
    return title_string

# Function to extract Product Price
def get_price(soup):
    try:
        price = soup.find("span",attrs={'class':"a-price aok-align-center"}).find("span",attrs={'class':"a-offscreen"}).text
    except AttributeError:
        try:
            price = soup.find("span",attrs={'class':"a-price aok-align-center"}).find("span",attrs={'class':"a-offscreen"}).text
        except:
            price = ""
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
        except:
            rating = ""	
    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        review_count = ""	
    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()
    except AttributeError:
        available = "Not Available"	
    return available

from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st
import numpy as np

# ... (your existing functions)

# Function to extract links
def get_links(soup):
    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    links_list = [link.get('href') for link in links]
    return links_list

# Streamlit App
def main():
    st.title("Amazon Web Scraper")

    # User input for the URL
    URL = st.text_input("Enter the URL:")

    if st.button("Scrape"):
        # Check if the URL is valid
        if not URL.startswith("https://www.amazon.com"):
            st.error("Invalid Amazon URL. Please enter a valid Amazon product search URL.")
            return

        # add your user agent
        HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                   'Accept-Language': 'en-US, en;q=0.5'}

        try:
            # HTTP Request
            webpage = requests.get(URL, headers=HEADERS)
            webpage.raise_for_status()

            # Soup Object containing all data
            soup = BeautifulSoup(webpage.content, "html.parser")

            # Get links
            links_list = get_links(soup)

            d = {"title": [], "price": [], "rating": [], "reviews": [], "availability": []}

            # Loop for extracting product details from each link
            for link in links_list:
                # Check if the link is an absolute URL
                if link.startswith("http"):
                    product_url = link
                else:
                    product_url = "https://www.amazon.com" + link

                new_webpage = requests.get(product_url, headers=HEADERS)
                new_webpage.raise_for_status()

                new_soup = BeautifulSoup(new_webpage.content, "html.parser")

                # Function calls to display all necessary product information
                d['title'].append(get_title(new_soup))
                d['price'].append(get_price(new_soup))
                d['rating'].append(get_rating(new_soup))
                d['reviews'].append(get_review_count(new_soup))
                d['availability'].append(get_availability(new_soup))

            amazon_df = pd.DataFrame.from_dict(d)
            amazon_df = amazon_df.dropna(subset=['title'])
            amazon_df['title'] = amazon_df['title'].replace('', np.nan)

            st.write("### Scraped Data:")
            st.write(amazon_df)

            # Save the dataframe to a CSV file
            csv_filename = "amazon_data.csv"
            amazon_df.to_csv(csv_filename, header=True, index=False)

            # Display the CSV file as a download link
            st.write("### Download CSV File:")
            st.markdown(f"[Download {csv_filename}](/{csv_filename})")

        except requests.exceptions.HTTPError as errh:
            st.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")

if __name__ == '__main__':
    main()
