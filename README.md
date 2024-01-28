# Real Estate Web Scraper

This Python project is a web scraper for real estate data in Switzerland from the website [homegate.ch](https://www.homegate.ch). The scraper gathers information about properties based on user-defined parameters such as type (buy or rent), city, price, and room count.

## Prerequisites

Before using the scraper, make sure you have the following prerequisites installed:

- Python 3
- PyQt5
- Peewee
- Requests
- Beautiful Soup
- Pandas
- NumPy
- Matplotlib
- Seaborn

You can install the required packages using the following command:

```bash
pip install PyQt5 peewee requests beautifulsoup4 pandas numpy matplotlib seaborn
```

## How to Use

1. Run the `main.py` script using Python:

   ```bash
   python main.py
   ```

2. The application window will appear with input fields for the following parameters:
   - **City**: Enter the name of the city for which you want to scrape real estate data.
   - **Price**: Select the price range from the dropdown list.
   - **Type**: Choose between "buy" and "rent".
   - **Room**: Select the number of rooms from the dropdown list.

3. Click on the "Choose Image Directory" button to select the directory where you want to save property images.

4. Click on the "Choose CSV Directory" button to select the directory where you want to save the CSV file containing property data.

5. Click the "Submit" button to start the web scraping process. The application will fetch real estate data based on your input parameters and save the data to a CSV file in the specified directory. Property images will be saved in the selected image directory.

## Database

The project uses a PostgreSQL database to store the scraped real estate data. The database is created using the `models.py` script, and the `HomeAds` model represents the structure of the stored data.

## Modules

- `modules.py`: Contains functions for web scraping, data extraction, and image downloading.
- `models.py`: Defines the Peewee model for the PostgreSQL database and initializes the database connection.
- `main.py`: The main script that creates the GUI using PyQt5, handles user input, and triggers the web scraping process.
