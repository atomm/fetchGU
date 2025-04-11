#!/usr/bin/env python
# .github/scripts/rss_to_csv.py

import os
import feedparser
import pandas as pd
from datetime import datetime
import csv

# Configuration
RSS_URL = os.environ.get('RSS_URL', 'https://example.com/feed.xml')
CSV_PATH = os.environ.get('CSV_PATH', 'data/rss_feed.csv')
MAX_ENTRIES = int(os.environ.get('MAX_ENTRIES', 10))

def ensure_directory_exists(file_path):
    """Create directory if it doesn't exist"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def parse_feed(url):
    """Parse the RSS feed and return a list of entries"""
    feed = feedparser.parse(url)
    entries = []
    
    for entry in feed.entries[:MAX_ENTRIES]:
        # Extract the basic information
        item = {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'fetch_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Try to get description/summary
        if 'description' in entry:
            item['description'] = entry.description
        elif 'summary' in entry:
            item['description'] = entry.summary
        else:
            item['description'] = ''
        
        entries.append(item)
    
    return entries

def append_to_csv(entries, csv_path):
    """Append new entries to CSV file, create if doesn't exist"""
    ensure_directory_exists(csv_path)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(csv_path)
    
    # Get existing URLs to avoid duplicates
    existing_urls = set()
    if file_exists:
        try:
            df = pd.read_csv(csv_path)
            if 'link' in df.columns:
                existing_urls = set(df['link'].tolist())
        except:
            # If there's an error reading the file (e.g., empty or corrupted)
            file_exists = False
    
    # Filter out entries that already exist in the CSV
    new_entries = [entry for entry in entries if entry['link'] not in existing_urls]
    
    if not new_entries:
        print("No new entries to add")
        return
    
    # Append new entries to the CSV
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_entries[0].keys())
        
        # Write header if file is newly created
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(new_entries)
    
    print(f"Added {len(new_entries)} new entries to {csv_path}")

def main():
    entries = parse_feed(RSS_URL)
    append_to_csv(entries, CSV_PATH)

if __name__ == "__main__":
    main()
