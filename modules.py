import re
import csv
import os
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import local_settings
import matplotlib.pyplot as plt
import seaborn as sns

from models import DatabaseManager, HomeAds


# Example of query: python main.py -t buy -c bern -p 5000000 -r 3
BASE_URL = "https://www.homegate.ch/{ad_type}/real-estate/city-{city}/matching-list?ac={room}&aj={price}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="""A simple command-line tool to
                       scrape Switzerland Real Estate
                       on wabsite https://homegate.ch
                       and its pages
                    """,
        epilog=f"Special thanks for using, for more support: {local_settings.SUPPORT}",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["buy", "rent"],
        help="set type: [buy, rent]",
        required=True,
    )
    parser.add_argument("-c", "--city", type=str, help="set city name", required=True)
    parser.add_argument("-p", "--price", type=int, help="set price", required=True)
    parser.add_argument(
        "-r", "--room", type=float, help="set room count", required=True
    )

    args = parser.parse_args()


def gather_data(ad_type, city, room, price):
    # "https://www.homegate.ch/{ad_type}/real-estate/city-{city}/matching-list?ac={room}&aj={price}"
    BASE_URL = (
        "https://www.homegate.ch/{0}/real-estate/city-{1}/matching-list?ac={2}&aj={3}"
    )
    URL = BASE_URL.format(ad_type, city, room, price)
    try:
        # Initial last page number which exist ads in it.
        last_page = find_last_page(URL)
        data = []  # A list of ads.
        # Iterate all posible urls
        for page in range(1, last_page + 1):
            # Creating page urls (add number of page to the url).
            url = URL + "&ep=" + str(page)
            # Extract all ads item from page 1 to last page.
            data.extend(find_all_ads(url))
    except Exception as e:
        print(e)
        print("Please check your input such as city name, price, room and ad_type.")
        print("Try Again!")
        exit()
    print("Crawling is Finished Successfully!")
    return data


# display plot base on data
def display_plot(data):
    # Generate axis values base on the count and specific column of dataframe
    def axis_lable_values(series, count):
        count_of_elements = count
        min_value = series.min()
        max_value = series.max()
        generated_list = np.linspace(min_value, max_value, count_of_elements)
        return generated_list

    df = pd.DataFrame(data)
    df = df[df["price"] != ""]
    df = df[df["room"] != ""]
    df = df[df["space"] != ""]
    df = df.dropna()
    if df.empty:
        print(
            "We can not display any chart, because there is not any ads or records in data frame."
        )
    else:
        df["price"] = df["price"].astype(int)
        df["space"] = df["space"].astype(int)
        df["room"] = df["room"].astype(float)
        # A plot to display price (CHF) of houses base on space (Square meters).
        plt.figure(figsize=(10, 6))
        plt.scatter(df["space"], df["price"])
        plt.yticks(sorted(axis_lable_values(df["price"], 10)), rotation=45)
        plt.xticks(sorted(axis_lable_values(df["space"], 10)), rotation=45)
        sns.regplot(x="space", y="price", data=df)
        # Set plot labels and title
        plt.xlabel("Size (Square meters)")
        plt.ylabel("Price (CHF)")
        plt.title("Regression of house price and house size")

        # Another plot to display price (CHF) of houses base on room count.
        plt.figure(figsize=(10, 6))
        grouped_df = df.groupby("room").agg({"price": "mean"}).reset_index()
        plt.plot(grouped_df["room"], grouped_df["price"])
        plt.title("Average price per number of rooms")
        plt.xlabel("room count")
        plt.ylabel("Price (CHF)")
        # Show the plot
        plt.show()


# Return all ads of a single page based on the query
def find_all_ads(url):
    response = requests.get(url, headers=headers)
    print("status code:", response.status_code, "Fetching url: " + response.url)
    soup = BeautifulSoup(response.text, "html.parser")
    list_of_item = soup.find_all(
        "div", {"role": "listitem", "data-test": "result-list-item"}
    )
    ads_in_a_page = []
    for item in list_of_item:
        ads_in_a_page.append(extrect_ad(item))
    return ads_in_a_page


# exteract all features of an ad(item) such as price, room, address, link, images and etc
def extrect_ad(item):
    # save_images(extract_image(item), extract_href(item).replace("/", ""))
    dict_of_data = {
        "href": extract_href(item),
        "price": extract_price(item),
        "image_urls": extract_image(item),
        "room": extract_room(item),
        "space": extract_space(item),
        "address": extract_address(item),
        "title": extract_title(item),
        "description": extract_description(item),
    }
    new_home_ad = HomeAds.create(
        href=extract_href(item),
        price=extract_price(item),
        image_urls=extract_image(item),
        room=extract_room(item),
        space=extract_space(item),
        address=extract_address(item),
        title=extract_title(item),
        description=extract_description(item),
    )
    new_home_ad.save()

    return dict_of_data


# Extract room count of an item (ad)
def extract_price(item):
    a_tags = item.find("a")
    price = a_tags.select('span[class^="HgListingCard_price"]')[0].text
    # price = a_tags.find("span", {"class": "HgListingCard_price_JoPAs"}).text
    price = "".join(filter(str.isdigit, price))
    return price


# Extract href of an item (ad)
def extract_href(item):
    a_tags = item.find("a")
    href = a_tags.get("href")
    return href


# Extract room count of an item (ad)
def extract_room(item):
    a_tags = item.find("a")
    parent_of_room_and_space = a_tags.select(
        'div[class^="HgListingRoomsLivingSpace_roomsLivingSpace"]'
    )[0]
    spans = parent_of_room_and_space.find_all("span")
    room = None
    for e in spans:
        if str(e).find("room") > 0:
            room = e.find("strong").text
    return room


# Extract space of an item (ad)
def extract_space(item):
    a_tags = item.find("a")
    parent_of_room_and_space = a_tags.select(
        'div[class^="HgListingRoomsLivingSpace_roomsLivingSpace"]'
    )[0]
    spans = parent_of_room_and_space.find_all("span")
    space = None
    for e in spans:
        if str(e).find("living space") > 0:
            space = e.find("strong").text
            space = re.findall(r"\d+", space)[0]
    return space


# Extract address of an item (ad)
def extract_address(item):
    a_tags = item.find("a")
    address = a_tags.find("address").text
    return address


# Extract description of an item (ad)
def extract_description(item):
    a_tags = item.find("a")
    p_tags = a_tags.select('p[class^="HgListingDescription"]')
    # Check if there is second tag p (because second tag p is description)
    if len(p_tags) > 1:
        description = p_tags[1].string
        return description
    else:
        return None


# Extract title of an item (ad)
def extract_title(item):
    a_tags = item.find("a")
    p_tags = a_tags.select('p[class^="HgListingDescription"]')
    # Check if there is first tag p (because first tag p is title)
    title = None
    if len(p_tags) > 0:
        title = p_tags[0].find("span").text
    return title


# Extract images of an item (ad)
def extract_image(item):
    a_tags = item.find("a")
    # Extract images of an ad
    pictures = a_tags.find_all("picture")
    image_urls = []
    for picture in pictures:
        pattern = re.compile(r"https[^ ]+\.jpg")
        # Find all matches in the input string
        image_urls.append(pattern.findall(str(picture)))
    return image_urls


# Save images to Disk in current dir
def save_images(lists_of_image_url, dir, user_dir):
    os.makedirs(os.path.join(user_dir, "images"), exist_ok=True)

    # Download and save each image
    for index, urls in enumerate(lists_of_image_url):
        # Check if list of url is not empty
        if len(urls) > 0:
            try:
                response = requests.get(urls[0])
                response.raise_for_status()  # Check for errors

                # Extract the filename from the URL
                first_path = os.path.join(user_dir, "images")
                path = os.path.join(first_path, dir)
                os.makedirs(path, exist_ok=True)
                filename = os.path.join(path, f"image_{index + 1}.jpg")

                # Save the image to the local disk
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Image {index + 1} saved as {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {index + 1}: {e}")


# Writing list of dictionaries to a CSV file
def save_data_as_csv(data, csv_file_name):
    filename = csv_file_name
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        # Extracting the column headers from the keys of the first dictionary
        fieldnames = data[0].keys()

        # Creating a CSV writer object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Writing the header row
        csv_writer.writeheader()

        # Writing the data rows
        csv_writer.writerows(data)
        print("CSV File Successfully Create!")


# Return the last pagination number and html contents of the given url
def find_last_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        print("status code:", response.status_code, "Fetching url:", url)
        soup = BeautifulSoup(response.text, "html.parser")
        pagination_nav = soup.find("nav", {"aria-label": "Pagination"})
        if pagination_nav:
            paginations = []
            pagination_links = pagination_nav.find_all("a")
            for link in pagination_links:
                if len(link.find_all("span")) > 0:
                    page = int(link.find_all("span")[0].string.replace("...", ""))
                    paginations.append(page)
            return int(max(paginations))
        else:
            print("there is no ad in this page")
            exit()
    except Exception as e:
        print("error: ", e)
    finally:
        return 1
