#!/usr/bin/env python3
"""
Ground Statistics Scraper for ESPN Cricinfo
Scrapes ground statistics data from ESPN Cricinfo ground pages
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GroundStatsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_ground_name(self, soup):
        """Extract ground name from the page"""
        try:
            # Try different selectors for ground name
            selectors = [
                'h1.ds-text-title-xl',
                'h1',
                '.ground-name',
                '.venue-name'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            
            # Fallback: extract from title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # Extract ground name from title like "Ground Name | ESPNCricinfo"
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
            
            return "Unknown Ground"
        except Exception as e:
            logger.error(f"Error extracting ground name: {e}")
            return "Unknown Ground"
    
    def extract_basic_info(self, soup):
        """Extract basic ground information"""
        info = {}
        
        try:
            # Look for ground details in various formats
            info_sections = soup.find_all(['div', 'section'], class_=re.compile(r'ground|venue|info'))
            
            for section in info_sections:
                text = section.get_text()
                
                # Extract capacity
                capacity_match = re.search(r'capacity[:\s]*(\d+(?:,\d+)*)', text, re.IGNORECASE)
                if capacity_match:
                    info['capacity'] = capacity_match.group(1).replace(',', '')
                
                # Extract location
                location_patterns = [
                    r'location[:\s]*([^,\n]+(?:,[^,\n]+)*)',
                    r'city[:\s]*([^,\n]+)',
                    r'country[:\s]*([^,\n]+)'
                ]
                
                for pattern in location_patterns:
                    location_match = re.search(pattern, text, re.IGNORECASE)
                    if location_match and 'location' not in info:
                        info['location'] = location_match.group(1).strip()
        
        except Exception as e:
            logger.error(f"Error extracting basic info: {e}")
        
        return info
    
    def extract_tables(self, soup):
        """Extract all statistical tables from the page"""
        tables_data = []
        
        try:
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables on the page")
            
            for i, table in enumerate(tables):
                try:
                    # Extract table caption/title
                    caption = ""
                    if table.find('caption'):
                        caption = table.find('caption').get_text(strip=True)
                    elif table.find_previous(['h2', 'h3', 'h4']):
                        caption = table.find_previous(['h2', 'h3', 'h4']).get_text(strip=True)
                    
                    # Extract headers
                    headers = []
                    header_row = table.find('tr')
                    if header_row:
                        for th in header_row.find_all(['th', 'td']):
                            headers.append(th.get_text(strip=True))
                    
                    # Extract data rows
                    rows = []
                    for tr in table.find_all('tr')[1:]:  # Skip header row
                        row = []
                        for td in tr.find_all(['td', 'th']):
                            cell_text = td.get_text(strip=True)
                            # Clean up cell text
                            cell_text = re.sub(r'\s+', ' ', cell_text)
                            row.append(cell_text)
                        if row:  # Only add non-empty rows
                            rows.append(row)
                    
                    if headers and rows:
                        table_data = {
                            'table_index': i,
                            'caption': caption,
                            'headers': headers,
                            'rows': rows,
                            'row_count': len(rows)
                        }
                        tables_data.append(table_data)
                        logger.info(f"Extracted table {i}: '{caption}' with {len(rows)} rows")
                
                except Exception as e:
                    logger.error(f"Error extracting table {i}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding tables: {e}")
        
        return tables_data
    
    def extract_match_results(self, soup):
        """Extract match results if available"""
        results = []
        
        try:
            # Look for match result patterns
            result_sections = soup.find_all(['div', 'section'], class_=re.compile(r'result|match|score'))
            
            for section in result_sections:
                # Extract match information
                match_info = {}
                text = section.get_text()
                
                # Look for score patterns
                score_pattern = r'(\d+(?:/\d+)?)\s*(?:&|\band\b)?\s*(\d+(?:/\d+)?)?'
                scores = re.findall(score_pattern, text)
                
                if scores:
                    match_info['scores'] = scores
                    results.append(match_info)
        
        except Exception as e:
            logger.error(f"Error extracting match results: {e}")
        
        return results
    
    def scrape_ground_stats(self, url):
        """Main method to scrape ground statistics"""
        logger.info(f"Starting to scrape: {url}")
        
        try:
            # Make request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            ground_name = self.extract_ground_name(soup)
            basic_info = self.extract_basic_info(soup)
            tables = self.extract_tables(soup)
            match_results = self.extract_match_results(soup)
            
            # Compile results
            ground_data = {
                'url': url,
                'ground_name': ground_name,
                'basic_info': basic_info,
                'tables': tables,
                'match_results': match_results,
                'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_tables': len(tables)
            }
            
            logger.info(f"Successfully scraped data for {ground_name}")
            logger.info(f"Found {len(tables)} tables and {len(match_results)} match results")
            
            return ground_data
        
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return None
    
    def save_to_json(self, data, filename):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_csv(self, data, base_filename):
        """Save tables to separate CSV files"""
        try:
            for i, table in enumerate(data.get('tables', [])):
                if table['rows']:
                    # Create DataFrame
                    df = pd.DataFrame(table['rows'], columns=table['headers'])
                    
                    # Clean filename
                    caption = table['caption'] or f"table_{i}"
                    safe_caption = re.sub(r'[^\w\s-]', '', caption).strip()
                    safe_caption = re.sub(r'[-\s]+', '_', safe_caption)
                    
                    filename = f"{base_filename}_{safe_caption}.csv"
                    df.to_csv(filename, index=False, encoding='utf-8')
                    logger.info(f"Table saved to {filename}")
        
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def print_summary(self, data):
        """Print a summary of scraped data"""
        if not data:
            print("No data to summarize")
            return
        
        print("\n" + "="*60)
        print(f"GROUND STATISTICS SUMMARY")
        print("="*60)
        print(f"Ground Name: {data['ground_name']}")
        print(f"URL: {data['url']}")
        print(f"Scrape Time: {data['scrape_timestamp']}")
        
        if data['basic_info']:
            print(f"\nBasic Information:")
            for key, value in data['basic_info'].items():
                print(f"  {key.title()}: {value}")
        
        print(f"\nTables Found: {data['total_tables']}")
        for i, table in enumerate(data['tables']):
            print(f"  Table {i+1}: {table['caption']} ({table['row_count']} rows)")
        
        if data['match_results']:
            print(f"\nMatch Results: {len(data['match_results'])} found")
        
        print("="*60)

def main():
    """Main function to run the scraper"""
    # Target URL
    url = "https://stats.espncricinfo.com/ci/engine/ground/56874.html?class=23;template=results;type=aggregate;view=results"
    
    # Initialize scraper
    scraper = GroundStatsScraper()
    
    # Scrape data
    print("🏏 Starting Ground Statistics Scraper...")
    data = scraper.scrape_ground_stats(url)
    
    if data:
        # Print summary
        scraper.print_summary(data)
        
        # Save data
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        ground_name_safe = re.sub(r'[^\w\s-]', '', data['ground_name']).strip()
        ground_name_safe = re.sub(r'[-\s]+', '_', ground_name_safe)
        
        # Save to JSON
        json_filename = f"ground_stats_{ground_name_safe}_{timestamp}.json"
        scraper.save_to_json(data, json_filename)
        
        # Save tables to CSV
        csv_base = f"ground_stats_{ground_name_safe}_{timestamp}"
        scraper.save_to_csv(data, csv_base)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"📁 Files saved with prefix: ground_stats_{ground_name_safe}_{timestamp}")
        
    else:
        print("❌ Scraping failed. Check the logs for details.")

if __name__ == "__main__":
    main()