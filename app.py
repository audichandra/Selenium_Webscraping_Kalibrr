from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io 
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests 
from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import seaborn as sb 
import numpy as np
import os

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this
has_scraped = False

#Initialize the Chrome driver
chrome_options = Options()
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chrome_options)

#insert the scrapping here
url = "https://www.kalibrr.id/job-board/te/data/1"
data = []

if not has_scraped:  # Check the has_scraped flag
    try:
        driver.get(url)
    
        while True:  # We'll keep this loop running until we break when there's no "next" button.
        
        # Extract job data from current page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.select('div[itemscope][itemtype="http://schema.org/ListItem"]')
            for job in jobs:
                title = job.select_one('h2 a').text
                desc = job.select_one('div.k-text-xs').text.strip()
                company = job.select_one('span.k-inline-flex a').text
                location = job.find('a', class_='k-text-subdued k-block')
                location = location.get_text(strip=True) if location else None
                posting_expiry = job.select_one('div.k-text-right span.k-block').text

                data.append([title, desc, company, location, posting_expiry])
        
        # Try to click the next button
            try:
                next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                aria_disabled = next_button.get_attribute('aria-disabled')
    
                if aria_disabled == 'true':
                    break  # Exit the loop if the next button is not clickable
    
                next_button.click()
                time.sleep(2)  # Give some time for the page to load

            except Exception as e:
                print(f"Error encountered: {e}")
                break

        has_scraped = True
        
    finally:
        driver.quit()
    
df = pd.DataFrame(data, columns=["title", "jobdesc", "company", "location", "posting and expiry"])


#insert data wrangling here
#Extracting dates 
def extract_dates(date_string):
    # Split the string into posting and expiry parts
    posting_part, expiry_part = date_string.split('•')
    
    # Extract details from each part
    posting_date = posting_part.strip().replace("Posted ", "").replace(" ago", "")
    expiry_date = expiry_part.strip().replace("Apply before ", "")
    
    return posting_date, expiry_date 

df['posting_date'], df['expiry_date'] = zip(*df['posting and expiry'].map(extract_dates))
df.drop(columns=['posting and expiry'], inplace=True)

# Convert 'Posting Date' to datetime format
today = datetime.today()
df['posting_date'] = df['posting_date'].str.extract('(\d+)')[0].fillna(0).astype(int)
df['posting_date'] = today - pd.to_timedelta(df['posting_date'], unit='D')
df['posting_date'] = pd.to_datetime(df['posting_date'].dt.date)

# Convert 'Expiry Date' to datetime format
df['expiry_date'] = df['expiry_date'] + ' ' + str(today.year)
df['expiry_date'] = pd.to_datetime(df['expiry_date'], format='%d %b %Y')

# Subsetting only available (non-expired) jobs
dfa = df[df['expiry_date'] > today]

# Creating and classifying the jobs available periods
dfa['days_between'] = (dfa['expiry_date'] - dfa['posting_date']).dt.days.astype(int)
def duration(days):
    if days < 30:
        return "< 1 month"
    elif 30 <= days < 60:
        return "1-2 months"
    elif 60 <= days < 90:
        return "2-3 months"
    else:
        return "> 3 months"

dfa['post_period'] = dfa['days_between'].apply(duration) 

# Creating and classifying the data-related jobs
pattern = r'(?i)data scientist|data engineer|quantitative|machine learning\b|\bML\b|\bAI\b|analyst|database|big data|ETL|cloud'
dfd = dfa[dfa['title'].str.contains(pattern, regex=True)].copy() 

def data_title(title):
    title_lower = title.lower()

    if any(keyword in title_lower for keyword in ['data scientist', 'machine learning', 'ml', 'ai', 'quantitative']):
        return 'Data Scientist'
    elif 'analyst' in title_lower:
        return 'Data Analyst'
    elif any(keyword in title_lower for keyword in ['data engineer','database', 'big data', 'etl', 'cloud']):
        return 'Data Engineer'
    else:
        return title  #Retaining those that did not match with any of the above

dfd['title'] = dfd['title'].apply(data_title)

# Extracting city and country inform,ation as well as subsetting Indonesian job postings
dfa['country'] = dfa['location'].str.split(',').str[-1].str.strip()
dfa['city'] = dfa['location'].str.split(',').str[0].str.strip()
dfi = dfa[dfa['country'] == 'Indonesia']

replacement_dict = {
    'Central Jakarta': ['Central Jakarta City', 'Kota Jakarta Pusat', 'Jakarta Pusat'],
    'South Jakarta': ['Jakarta Selatan', 'Kota Jakarta Selatan', 'South Jakarta City'],
    'West Jakarta': ['Jakarta Barat', 'Kota Jakarta Barat'],
    'North Jakarta': ['Jakarta Utara'],
    'East Jakarta': ['Jakarta Timur'],
    'Bandung': ['Bandung Kota'],
    'Tangerang': ['Tangerang Kota'],
    'South Tangerang': ['Tangerang Selatan', 'Kota Tangerang Selatan']
}

for standardized, variations in replacement_dict.items():
    for variant in variations:
        dfi['city'] = dfi['city'].replace(variant, standardized)

# Creating country column in data-related jobs dataframe for post period and title analysis
dfd['country'] = dfd['location'].str.split(',').str[-1].str.strip()

# Frequency table based on post period, data-related jobs and locations
dfg1 = dfa['post_period'].value_counts().reset_index()
dfg2 = dfd['title'].value_counts().reset_index() 
dfg3 = dfi['city'].value_counts().reset_index()

# Frequency tables of comparison between Indonesia and other countries in post period and data-related jobs title
dfg4 = dfd.groupby('country')['post_period'].value_counts().unstack().fillna(0).stack().reset_index(name='count')
dfg5 = dfd.groupby('country')['title'].value_counts().groupby(level=0).head().reset_index() 
 
# Plot function
def custom_barplot(data, x_col, y_col, hue_col=None, order=None, title='', xlabel='', ylabel='', xrotation=None, hue_title_size=14):
    """
    Custom bar plot function with annotations.
    
    Parameters:
    - data: DataFrame containing the data
    - x_col: Name of the column to be plotted on the x-axis
    - y_col: Name of the column to be plotted on the y-axis
    - hue_col: Name of the column for hue differentiation (default is None)
    - order: Order for the x-axis values (default is None)
    - title: Title of the plot
    - xlabel: Label for the x-axis
    - ylabel: Label for the y-axis
    - xrotation: Rotation for the x-axis 
    - hue_title_size: Size of the hue title
    """
    
    # Common Parameters
    color = sb.color_palette("deep")[0]
    title_fontsize = 15
    axis_label_fontsize = 12

    plt.figure(figsize=(15, 12))
    if hue_col:
        ax = sb.barplot(data=data, x=x_col, y=y_col, hue=hue_col, palette='deep', order=order)
    else:
        ax = sb.barplot(data=data, x=x_col, y=y_col, color=color, order=order)
        
    # Annotating bars with their values
    for p in ax.patches:
        height = p.get_height()
        if not np.isnan(height):  # Check if the height is not NaN
            ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')

    # Setting titles and labels
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel(xlabel, fontsize=axis_label_fontsize)
    plt.ylabel(ylabel, fontsize=axis_label_fontsize)
    plt.xticks(rotation=xrotation, fontsize=axis_label_fontsize)
    plt.yticks(fontsize=axis_label_fontsize)
    if hue_col:
        legend = plt.legend(title=hue_col, fontsize=axis_label_fontsize)
        legend.get_title().set_fontsize(hue_title_size) 

def plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_base64


def create_base64():
    ordered_period = ['< 1 month', '1-2 months', '2-3 months', '> 3 months']
    
    base64_images = []

    try:
        custom_barplot(dfg1, 'post_period', 'count', order=ordered_period, title='Job Posting Active Period Distribution', xlabel='Post Period', ylabel='Count')
        img_str = plot_to_base64()
        base64_images.append(img_str)
        plt.close()
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        custom_barplot(dfg2, 'title', 'count', title='Data-related Job Posting Distribution', xlabel='Title', ylabel='Count')
        img_str = plot_to_base64()
        base64_images.append(img_str)
        plt.close()
    except Exception as e:
        print(f"Error: {e}")

    try:
        custom_barplot(dfg3.head(10), 'city', 'count', title='Job Posting Distribution in Top 10 Cities', xlabel='City', ylabel='Count', xrotation=35)
        img_str = plot_to_base64()
        base64_images.append(img_str)
        plt.close()
    except Exception as e:
        print(f"Error: {e}")

    try:
        custom_barplot(dfg4, 'post_period', 'count', 'country', order=ordered_period, title='Distribution of Data-related Job Posting Durations in Indonesia and Others', xlabel='Posting Period', ylabel='Number of Jobs')
        img_str = plot_to_base64()
        base64_images.append(img_str)
        plt.close()
    except Exception as e:
        print(f"Error: {e}")

    try:
        custom_barplot(dfg5, 'title', 'count', 'country', title='Distribution of Data-related Job Posting in Indonesia and Others', xlabel='Job Titles', ylabel='Number of Jobs')
        img_str = plot_to_base64()
        base64_images.append(img_str)
        plt.close() 
    except Exception as e:
        print(f"Error: {e}")

    return base64_images

#end of data wranggling 

@app.route("/")
def index():
    try:
        base64_images = create_base64()
    except Exception as e:
        print(f"Error encountered while creating and saving plots: {e}")
        base64_images = []
    return render_template('index.html', images=base64_images)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)