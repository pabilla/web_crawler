# Web Crawler

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Handling Failed URLs](#handling-failed-urls)

## Overview

**Web Crawler** is a robust and flexible web scraping tool built with [Scrapy](https://scrapy.org/). It is designed to efficiently crawl specified websites, extract relevant content, handle errors gracefully, and save the extracted data either locally or on Amazon S3. This project is ideal for collecting large-scale web data for various applications such as data analysis, research, and monitoring.

## Features

- **Dynamic Crawling**: Follows links within specified domains while respecting exclusion rules.
- **Content Extraction**: Extracts titles, URLs, and main content from web pages, excluding unwanted sections like headers, footers, and advertisements.
- **Error Handling**: Custom middleware manages HTTP errors and network exceptions with retry mechanisms.
- **Flexible Data Saving**: Save extracted data locally or on Amazon S3 with configurable settings.
- **Data Cleaning**: Cleans and validates extracted text to ensure data quality.
- **Respect for `robots.txt`**: Adheres to website crawling rules to ensure ethical scraping practices.
- **Logging**: Comprehensive logging for monitoring crawler activities and debugging.

## Project Structure

- **spiders/**: Contains spider definitions.
  - `main_spider.py`: The primary spider responsible for crawling and data extraction.
  - `file_savers.py`: Handles saving data to local files or S3.
- **items.py**: Defines the data models (`WebCrawlerItem` and `FailedItem`).
- **middlewares.py**: Custom middleware for error handling.
- **pipelines.py**: Processes and cleans extracted items before saving.
- **settings.py**: Scrapy settings and configurations.
- **data.jsonl**: Stores successfully scraped data.
- **failed.jsonl**: Logs URLs that failed to be scraped.

## Installation

### Prerequisites

- Python 3.7 or higher
- [Scrapy](https://scrapy.org/)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (if using S3 for data storage)

### Steps

1. **Clone the Repository**

```bash
   git clone https://github.com/pabilla/web_crawler.git
   cd web_crawler
 ```
   
2. **Create a Virtual Environment**

```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate 
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure AWS Credentials (If Using S3)**

Ensure that your AWS credentials are set up. You can configure them using the AWS CLI or by setting environment variables.

```bash
aws configure
```

## Configuration

All configurations are managed via the `settings.py` file. Below are the key configurations you can adjust:

**File Saver Configuration**   

- Local Storage :
```python
FILESAVER_CONFIG = {
    "type": "local",  # Change to 'local'
    "directory_path": "./web_crawler",  # Directory to save final_data
    "filename": "final_data.jsonl",
}
```
- Amazon S3 :
```python
FILESAVER_CONFIG = {
    "type": "s3",  # Change to 's3'
    "filename": "final_data.jsonl",
    "s3_bucket": "your-s3-bucket-name",  # Replace with your S3 bucket
    "upload_interval": 10  # Number of items before uploading
}
```

**Failed File Saver Configuration**
Similar to `FILESAVER_CONFIG`, you can configure how to save failed URLs.

- Local Storage :

```python
FAILED_FILESAVER_CONFIG = {
    "type": "local",
    "directory_path": "./web_crawler",
    "filename": "failed.jsonl",
}
```
- Amazon S3 :

```python
FAILED_FILESAVER_CONFIG = {
    "type": "s3",
    "filename": "failed.jsonl",
    "s3_bucket": "your-s3-bucket-name",
}
```

**Other Settings**

- **User-Agent:** Customize the user-agent string to mimic different browsers.
- **Concurrency & Delay:** Adjust `CONCURRENT_REQUESTS` and `DOWNLOAD_DELAY` to control the crawling speed.
- **Retry Settings:** Configure `RETRY_TIMES` and `RETRY_HTTP_CODES` for handling retries on failed requests.
- **Robots.txt:** Set `ROBOTSTXT_OBEY` to `True` to respect crawling rules.

## Usage

**Running the Crawler:**

Navigate to the project directory and execute the following command:

```bash
scrapy crawl web_crawler
```
**Customizing Start URLs:**  

By default, the crawler starts with a predefined list of URLs. To customize, edit the `start_urls` list in `main_spider.py`:

```python
start_urls = [
    'https://www.example.com/',
    'https://www.anotherexample.com/',
    # Add more URLs as needed
]
```
**Adjusting Crawl Rules:**  

Modify the `rules` in `main_spider.py` to include or exclude specific URL patterns or file extensions.

## Handling Failed URLs
Failed URLs are logged in `failed.jsonl` (or your configured location). This allows you to review and reprocess them if necessary.

**Example Entry**
```json
{
    "failed_url": "https://www.example.com/nonexistent-page",
    "error_code": 404
}
```
## Keyword extraction

We implemented a keyword extraction with NLTK and Scikit-Learn librairies

## Configure ElasticSearch

Configuration of ElasticSearch on Docker using docker-compose and configuration files into /elastic

## Web App

Designing a web app allowing user to query the data from ElasticSearch index