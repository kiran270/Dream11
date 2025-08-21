# Ground Statistics Scraper

This script scrapes cricket ground statistics from ESPN Cricinfo ground pages.

## Files

1. **`ground_stats_scraper.py`** - Full-featured scraper with advanced options
2. **`simple_ground_scraper.py`** - Simple, focused scraper for quick use
3. **`requirements_scraper.txt`** - Required Python packages

## Installation

```bash
# Install required packages
pip install -r requirements_scraper.txt

# Or install manually
pip install requests beautifulsoup4 pandas lxml
```

## Usage

### Simple Scraper (Recommended)

```bash
python simple_ground_scraper.py
```

This will scrape the default URL and save data to JSON format.

### Advanced Scraper

```bash
python ground_stats_scraper.py
```

This provides more features including CSV export and detailed analysis.

## Customizing URLs

To scrape different grounds, modify the URL in the script:

```python
# Example URLs:
# Lord's: https://stats.espncricinfo.com/ci/engine/ground/57.html?class=23;template=results;type=aggregate;view=results
# MCG: https://stats.espncricinfo.com/ci/engine/ground/348.html?class=23;template=results;type=aggregate;view=results
# Eden Gardens: https://stats.espncricinfo.com/ci/engine/ground/56874.html?class=23;template=results;type=aggregate;view=results
```

## Output

The scraper will create:

1. **JSON file** - Complete data structure with all tables
2. **CSV files** (advanced scraper) - Individual CSV files for each table
3. **Console output** - Summary of scraped data

## Example Output Structure

```json
{
  "ground_name": "Eden Gardens, Kolkata",
  "url": "https://stats.espncricinfo.com/...",
  "scrape_time": "2025-08-20 14:30:45",
  "tables": [
    {
      "index": 0,
      "caption": "Team records",
      "headers": ["Team", "Mat", "Won", "Lost", "Tied", "NR", "%"],
      "data": [
        ["India", "50", "35", "12", "1", "2", "72.91"],
        ["Australia", "25", "15", "8", "0", "2", "65.21"]
      ],
      "row_count": 10,
      "column_count": 7
    }
  ]
}
```

## Features

- **Automatic table detection** - Finds all statistical tables on the page
- **Header extraction** - Captures column headers properly
- **Data cleaning** - Removes extra whitespace and formats data
- **Error handling** - Continues scraping even if some tables fail
- **Multiple formats** - Saves data in JSON and CSV formats
- **Progress tracking** - Shows scraping progress in console

## Troubleshooting

1. **Connection errors**: Check internet connection and URL accessibility
2. **Empty results**: The page structure might have changed
3. **Missing data**: Some tables might not have standard HTML structure

## Legal Note

This scraper is for educational and personal use. Please respect ESPN Cricinfo's terms of service and robots.txt file. Consider adding delays between requests if scraping multiple pages.