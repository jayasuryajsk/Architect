"""
Real Web Access and Data Collection Tools
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import feedparser

logger = logging.getLogger(__name__)


class WebDataCollector:
    """Collects real data from the web"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL"""
        try:
            async with self.session.get(url, timeout=30) as response:
                content = await response.text()
                
                return {
                    'url': url,
                    'status': response.status,
                    'content': content,
                    'headers': dict(response.headers),
                    'content_type': response.content_type
                }
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'status': 0
            }
    
    async def fetch_json_api(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Fetch JSON data from API"""
        try:
            async with self.session.get(url, params=params, timeout=30) as response:
                data = await response.json()
                
                return {
                    'url': url,
                    'status': response.status,
                    'data': data,
                    'success': True
                }
        except Exception as e:
            logger.error(f"Error fetching JSON from {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    async def search_web(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo HTML parsing"""
        # Using DuckDuckGo HTML version as it doesn't require API key
        search_url = "https://html.duckduckgo.com/html/"
        
        try:
            async with self.session.post(
                search_url,
                data={'q': query},
                timeout=30
            ) as response:
                html = await response.text()
                
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'position': len(results) + 1
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
    
    async def extract_structured_data(self, url: str) -> Dict[str, Any]:
        """Extract structured data from a webpage"""
        response = await self.fetch_url(url)
        
        if response.get('status') != 200:
            return {'error': 'Failed to fetch page'}
            
        soup = BeautifulSoup(response['content'], 'html.parser')
        
        # Extract various structured data
        data = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'meta': {},
            'headings': {},
            'links': [],
            'images': [],
            'tables': [],
            'lists': []
        }
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                data['meta'][name] = content
        
        # Headings
        for level in range(1, 4):
            headings = [h.get_text(strip=True) for h in soup.find_all(f'h{level}')]
            if headings:
                data['headings'][f'h{level}'] = headings
        
        # Links
        for link in soup.find_all('a', href=True)[:50]:  # Limit to 50
            data['links'].append({
                'text': link.get_text(strip=True),
                'url': urljoin(url, link['href'])
            })
        
        # Images
        for img in soup.find_all('img', src=True)[:20]:  # Limit to 20
            data['images'].append({
                'src': urljoin(url, img['src']),
                'alt': img.get('alt', '')
            })
        
        # Tables
        for table in soup.find_all('table')[:5]:  # Limit to 5 tables
            table_data = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)
            if table_data:
                data['tables'].append(table_data)
        
        # Lists
        for ul in soup.find_all(['ul', 'ol'])[:10]:  # Limit to 10 lists
            items = [li.get_text(strip=True) for li in ul.find_all('li')]
            if items:
                data['lists'].append(items)
        
        return data
    
    async def monitor_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Monitor RSS feed for updates"""
        try:
            # Fetch feed content
            response = await self.fetch_url(feed_url)
            
            if response.get('status') != 200:
                return []
                
            # Parse feed
            feed = feedparser.parse(response['content'])
            
            entries = []
            for entry in feed.entries[:20]:  # Limit to 20 entries
                entries.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'author': entry.get('author', '')
                })
            
            return entries
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            return []


class RealEstateDataCollector:
    """Specialized collector for real estate data"""
    
    def __init__(self):
        self.web_collector = WebDataCollector()
        
    async def collect_market_data(self, location: str) -> Dict[str, Any]:
        """Collect real estate market data for a location"""
        data = {
            'location': location,
            'collected_at': datetime.utcnow().isoformat(),
            'sources': [],
            'metrics': {}
        }
        
        async with self.web_collector as collector:
            # Search for market data
            search_queries = [
                f"{location} median house price 2024",
                f"{location} rental yield property market",
                f"{location} real estate market trends",
                f"{location} property auction clearance rates"
            ]
            
            for query in search_queries:
                results = await collector.search_web(query, num_results=5)
                
                for result in results:
                    data['sources'].append({
                        'query': query,
                        'title': result['title'],
                        'url': result['url'],
                        'snippet': result['snippet']
                    })
                    
                    # Extract numbers from snippets
                    numbers = re.findall(r'\$[\d,]+(?:\.\d+)?[MmKk]?|\d+(?:\.\d+)?%', result['snippet'])
                    if numbers:
                        data['metrics'][query] = numbers
            
            # Try to fetch government statistics
            if 'sydney' in location.lower():
                # NSW government data
                stats_url = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities"
                page_data = await collector.extract_structured_data(stats_url)
                data['government_source'] = page_data
                
            elif 'canberra' in location.lower():
                # ACT government data
                stats_url = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities"
                page_data = await collector.extract_structured_data(stats_url)
                data['government_source'] = page_data
        
        return data
    
    async def compare_markets(self, location1: str, location2: str) -> Dict[str, Any]:
        """Compare two real estate markets"""
        # Collect data for both locations in parallel
        data1_task = asyncio.create_task(self.collect_market_data(location1))
        data2_task = asyncio.create_task(self.collect_market_data(location2))
        
        data1, data2 = await asyncio.gather(data1_task, data2_task)
        
        comparison = {
            'locations': [location1, location2],
            'data': {
                location1: data1,
                location2: data2
            },
            'analysis': self._analyze_market_data(data1, data2)
        }
        
        return comparison
    
    def _analyze_market_data(self, data1: Dict, data2: Dict) -> Dict[str, Any]:
        """Analyze and compare market data"""
        analysis = {
            'data_quality': {
                data1['location']: len(data1['sources']),
                data2['location']: len(data2['sources'])
            },
            'common_metrics': {},
            'insights': []
        }
        
        # Extract common metrics
        for key in data1.get('metrics', {}):
            if key in data2.get('metrics', {}):
                analysis['common_metrics'][key] = {
                    data1['location']: data1['metrics'][key],
                    data2['location']: data2['metrics'][key]
                }
        
        # Generate insights
        if len(data1['sources']) > len(data2['sources']):
            analysis['insights'].append(
                f"More data available for {data1['location']} ({len(data1['sources'])} sources) "
                f"compared to {data2['location']} ({len(data2['sources'])} sources)"
            )
        
        return analysis


# Standalone tool functions that can be generated and used by the agent

async def search_web_tool(query: str, num_results: int = 10) -> Dict[str, Any]:
    """Search the web and return results"""
    async with WebDataCollector() as collector:
        results = await collector.search_web(query, num_results)
        
        return {
            "result": results,
            "metadata": {
                "query": query,
                "num_results": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
        }


async def fetch_webpage_content(url: str) -> Dict[str, Any]:
    """Fetch and parse webpage content"""
    async with WebDataCollector() as collector:
        data = await collector.extract_structured_data(url)
        
        return {
            "result": data,
            "metadata": {
                "url": url,
                "fetched_at": datetime.utcnow().isoformat()
            }
        }


async def collect_real_estate_data(location: str) -> Dict[str, Any]:
    """Collect real estate market data for a location"""
    collector = RealEstateDataCollector()
    data = await collector.collect_market_data(location)
    
    return {
        "result": data,
        "metadata": {
            "location": location,
            "sources_found": len(data['sources']),
            "metrics_extracted": len(data['metrics'])
        }
    }


async def compare_housing_markets(location1: str, location2: str) -> Dict[str, Any]:
    """Compare housing markets between two locations"""
    collector = RealEstateDataCollector()
    comparison = await collector.compare_markets(location1, location2)
    
    return {
        "result": comparison,
        "metadata": {
            "locations": [location1, location2],
            "total_sources": sum(len(d['sources']) for d in comparison['data'].values()),
            "comparison_generated": True
        }
    }