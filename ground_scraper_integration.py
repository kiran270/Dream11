#!/usr/bin/env python3
"""
Ground Scraper Integration for Match Creation
Integrates ground scraping with match creation process
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from ground_analyzer import GroundAnalyzer
from db import save_ground_analysis

def scrape_and_analyze_ground(url, match_id):
    """Scrape ground data and analyze it for a specific match"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🏏 Scraping ground data from: {url}")
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
        
        # Analyze the scraped data
        analyzer = GroundAnalyzer()
        analyzer.ground_data = ground_data
        analysis = analyzer.analyze_ground_conditions()
        
        if analysis:
            print(f"🎯 Ground Analysis Complete:")
            print(f"   Type: {analysis.get('ground_type', 'Unknown')}")
            print(f"   RPO: {analysis.get('avg_runs_per_over', 0):.2f}")
            
            # Save to database
            if save_ground_analysis(match_id, analysis):
                print("✅ Ground analysis saved to database")
            else:
                print("❌ Failed to save ground analysis")
            
            return analysis
        else:
            print("❌ Failed to analyze ground data")
            return None
        
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return None

def get_ground_url_suggestions():
    """Get common ground URL patterns for user reference"""
    suggestions = [
        {
            'ground': 'Eden Gardens, Kolkata',
            'url': 'https://stats.espncricinfo.com/ci/engine/ground/56874.html?class=23;template=results;type=aggregate;view=results'
        },
        {
            'ground': 'Lord\'s, London',
            'url': 'https://stats.espncricinfo.com/ci/engine/ground/57.html?class=23;template=results;type=aggregate;view=results'
        },
        {
            'ground': 'MCG, Melbourne',
            'url': 'https://stats.espncricinfo.com/ci/engine/ground/348.html?class=23;template=results;type=aggregate;view=results'
        },
        {
            'ground': 'Wankhede Stadium, Mumbai',
            'url': 'https://stats.espncricinfo.com/ci/engine/ground/58.html?class=23;template=results;type=aggregate;view=results'
        }
    ]
    return suggestions

def validate_cricinfo_url(url):
    """Validate if URL is a valid ESPN Cricinfo ground URL"""
    if not url:
        return False
    
    # Check if it's a cricinfo URL
    if 'espncricinfo.com' not in url and 'cricinfo.com' not in url:
        return False
    
    # Check if it contains ground pattern
    if '/ground/' not in url:
        return False
    
    return True

if __name__ == "__main__":
    # Test the integration
    test_url = "https://stats.espncricinfo.com/ci/engine/ground/56874.html?class=23;template=results;type=aggregate;view=results"
    test_match_id = 999  # Test match ID
    
    result = scrape_and_analyze_ground(test_url, test_match_id)
    if result:
        print("✅ Integration test successful")
    else:
        print("❌ Integration test failed")