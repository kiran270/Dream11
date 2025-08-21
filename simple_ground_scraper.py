#!/usr/bin/env python3
"""
Simple Ground Statistics Scraper for ESPN Cricinfo
Focused scraper for the specific URL format
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_ground_stats(url):
    """Scrape ground statistics from ESPN Cricinfo"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🏏 Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract ground name
        ground_name = "Unknown Ground"
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            if '|' in title_text:
                ground_name = title_text.split('|')[0].strip()
        
        print(f"📍 Ground: {ground_name}")
        
        # Extract all tables
        tables = soup.find_all('table')
        print(f"📊 Found {len(tables)} tables")
        
        ground_data = {
            'ground_name': ground_name,
            'url': url,
            'scrape_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tables': []
        }
        
        for i, table in enumerate(tables):
            try:
                # Get table caption/title
                caption = f"Table {i+1}"
                if table.find('caption'):
                    caption = table.find('caption').get_text(strip=True)
                elif table.find_previous(['h2', 'h3', 'h4']):
                    prev_heading = table.find_previous(['h2', 'h3', 'h4'])
                    if prev_heading:
                        caption = prev_heading.get_text(strip=True)
                
                # Extract headers
                headers = []
                header_row = table.find('tr')
                if header_row:
                    for cell in header_row.find_all(['th', 'td']):
                        headers.append(cell.get_text(strip=True))
                
                # Extract data rows
                rows = []
                for tr in table.find_all('tr')[1:]:  # Skip header
                    row = []
                    for cell in tr.find_all(['td', 'th']):
                        text = cell.get_text(strip=True)
                        text = re.sub(r'\s+', ' ', text)  # Clean whitespace
                        row.append(text)
                    if row and any(row):  # Only add non-empty rows
                        rows.append(row)
                
                if headers and rows:
                    table_data = {
                        'index': i,
                        'caption': caption,
                        'headers': headers,
                        'data': rows,
                        'row_count': len(rows),
                        'column_count': len(headers)
                    }
                    ground_data['tables'].append(table_data)
                    print(f"  ✅ {caption}: {len(rows)} rows × {len(headers)} columns")
                
            except Exception as e:
                print(f"  ❌ Error processing table {i}: {e}")
                continue
        
        return ground_data
        
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return None

def save_data(data, filename_base):
    """Save data to JSON and print summary"""
    if not data:
        return
    
    # Save to JSON
    json_filename = f"{filename_base}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Data saved to: {json_filename}")
    
    # Print summary
    print(f"\n📋 SUMMARY:")
    print(f"Ground: {data['ground_name']}")
    print(f"Tables: {len(data['tables'])}")
    print(f"Scrape Time: {data['scrape_time']}")
    
    for table in data['tables']:
        print(f"  • {table['caption']}: {table['row_count']} rows")
    
    return json_filename

def main():
    """Main execution"""
    url = "https://stats.espncricinfo.com/ci/engine/ground/56874.html?class=23;template=results;type=aggregate;view=results"
    
    # Scrape data
    data = scrape_ground_stats(url)
    
    if data:
        # Generate filename
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename_base = f"ground_stats_{timestamp}"
        
        # Save and display results
        save_data(data, filename_base)
        
        print(f"\n🎉 Scraping completed successfully!")
        
        # Show first few rows of first table as example
        if data['tables']:
            first_table = data['tables'][0]
            print(f"\n📊 Sample from '{first_table['caption']}':")
            print("Headers:", first_table['headers'])
            for i, row in enumerate(first_table['data'][:3]):  # First 3 rows
                print(f"Row {i+1}:", row)
            if len(first_table['data']) > 3:
                print(f"... and {len(first_table['data']) - 3} more rows")
    
    else:
        print("❌ Failed to scrape data")

if __name__ == "__main__":
    main()