import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import random

class AyurvedicImageScraper:
    def __init__(self):
        load_dotenv()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _sanitize_query(self, query):
        """Sanitize and contextualize the query for Ayurvedic image search."""
        ayurvedic_keywords = [
            "herbal", "natural remedy", "traditional medicine", 
            "ayurvedic", "holistic healing"
        ]
        return f"{random.choice(ayurvedic_keywords)} {query}"

    def fetch_images(self, query, num_images=4):
        """
        Fetch Ayurvedic related images from Google Images.
        
        Args:
            query (str): Search term
            num_images (int): Number of images to fetch
        
        Returns:
            list: List of image URLs
        """
        sanitized_query = self._sanitize_query(query)
        search_url = f"https://www.google.com/search?q={sanitized_query}&tbm=isch"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            image_tags = soup.find_all('img')
            image_urls = [
                img.get('src') or img.get('data-src')
                for img in image_tags 
                if img.get('src') and 'http' in str(img.get('src'))
            ]
            
            # Filter and return valid image URLs
            valid_urls = [
                url for url in image_urls 
                if url and not url.endswith('.svg') and not url.startswith('data:')
            ][:num_images]
            
            return valid_urls or [
                "https://via.placeholder.com/300?text=Ayurvedic+Image"
            ]
        
        except Exception as e:
            print(f"Image fetch error: {e}")
            return [
                "https://via.placeholder.com/300?text=Ayurvedic+Image"
            ]

