# Selenium_Webscraping_Kalibrr

## Table of Contents
- [Description](#description)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [File Structure](#file-structure)
- [Usage](#usage)
- [Results](#results)
- [Acknowledgements](#acknowledgements)

## Description
This project showcases web scraping of job postings from the Kalibrr website using a combination of BeautifulSoup and Selenium. It provides a deep dive into extracting relevant job data and serves as a guide on using these tools effectively together and deploying it on Flask app.

ain project milestones:
1. **Setting Up the Web Scraping Environment**: Preparing your system for scraping with Selenium and BeautifulSoup.
2. **Data Extraction**: Accessing and extracting relevant job posting data from Kalibrr.
3. **Data Visualization**: Creating plots based on the extracted data 
4. **Data Presentation**: Using Flask to visually present scraped data.

## Getting Started

### Prerequisites
- Python 3.10
- A compatible web browser (e.g., Chrome, if using ChromeDriver with Selenium)
- Jupyter Notebook (optional)

### Installation
To set up the environment:
1. Clone this repository:  
   `git clone <repo-link>`
2. Navigate to the directory:  
   `cd <repo-name>`
3. Install the required packages:  
   `pip install -r requirements.txt`

## File Structure
- `img/` : Contains the image file for the example that are used in readme.md 
- `templates/`: Contains HTML files for Flask visualization.
- `static/`: Contains static resources like CSS and JavaScript for Flask.
- `Selenium web scraping Kalibrr.py`: Python script detailing the web scraping process.
- `app.py`: Flask application script to showcase the results.
- `README.md`: The file you're currently reading.

## Usage
After you installed the required packages, you can navigate into `app.py` file manually and run it. Then, open your browser and navigate to http://127.0.0.1:5000 to see the visualized job listing data.
For a detailed explanation and code walkthrough, please refer to [Selenium Webscraping Kalibrr Notebook](https://github.com/audichandra/Selenium_Webscraping_Kalibrr/blob/main/Selenium%20web%20scraping%20Kalibrr.ipynb).

## Results
Below are some visual results obtained from the scraped data:

![Job Distribution by Location](https://github.com/audichandra/Selenium_Webscraping_Kalibrr/blob/main/img/dfg3.png)

This graph shows the distribution of job postings by Indonesia top 10 areas, indicating the cities with the highest demand 

![Job Posting Period Distribution](https://github.com/audichandra/Selenium_Webscraping_Kalibrr/blob/main/img/dfg1.png)

The above visualization gives insights into how long the companies will open their job postings  

![Job Posting Distribution based on Data Roles](https://github.com/audichandra/Selenium_Webscraping_Kalibrr/blob/main/img/dfg2.png)

## Acknowledgements
- **Authors**: Audi Chandra  
- **License**: [MIT License](https://github.com/audichandra/Selenium_Webscraping_Kalibrr/blob/main/LICENSE) 
- A nod to [**Kalibrr**](https://www.kalibrr.id/id-ID/job-board/te/data/1) for providing a platform filled with rich job posting data.
- Heartfelt gratitude to [**Algoritma Data Science School**](https://gitlab.com/algoritma4students/academy-python/capstone/web_scraping) for making available the base example of the project and providing learning opportunity.

