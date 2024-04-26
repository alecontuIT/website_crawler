from bs4 import BeautifulSoup as bs
from typing import List
import requests
import json
import sys

from plotter import *
from llm_api import *

class WebCrawler:
    def __init__(self, home_url: str, llm: bool = False, llm_kind: str = 'summarizer'):
        self._home_url = home_url
        self._homepage = bs(requests.get(home_url).text, 'html.parser')
        try:
            self._header = self._homepage.find('header')
        except:
            self._header = []
        try:
            self._footer = self._homepage.find('footer')
        except:
            self._footer = []
        self._homepage_urls = list(dict.fromkeys(self.get_all_urls(self._homepage)))
        # Data structure containing (url : [url_list]) pairs
        # url is the url of the page
        # url_list is the list of URLs contained in the page
        self.urls_network = {
            self._home_url : self._homepage_urls,
        }
        # Data structures containing (url : num) pairs
        # url is the url of the page
        # num is the number of times the page is present in the website
        # This data structure is used to have all the URLs present
        # in the website, plus the number of time it has been cited
        self.listed_url = {}
        # Queue of URLs to visit
        self._queue = []
        
        try:
            self.header_urls = self.get_all_urls(self._header)
        except:
            self.header_urls = []
        try:
            self.footer_urls = self.get_all_urls(self._footer)
        except:
            self.footer_urls = []
        
        self.llm = bool(llm)
        if self.llm:
            self.llm_kind = llm_kind
            self.llm_response = {}
            if self.llm_kind == 'summarizer':
                self.llmSummarizer = llmSummarizer()
            elif self.llm_kind == 'seo_optimizer':
                self.llmSeoOptimizer = llmSeoOptimizer()
            else:
                raise "Wrong 'llm_kind' selected: try 'summarizer' or 'seo_optimizer'. "
            
        
    def get_all_urls(self, html:str)->List[str]:
        '''
        Given the html of a page, it returns all the signle URLs contained
        '''
        urls = []
        for link in html.findAll('a', href=True):
            url = link['href']
            # Take only URLs of the same website
            if url[:len(self._home_url)] == self._home_url:
                if ('#' not in url) and ('login' not in url):
                    urls.append(url)
            elif ('https://' in url or 'http://'in url):
                # External website
                pass
            else:
                # Inner website URL formatted in a short format
                url = self._home_url+url
                if ('#' not in url) and ('login' not in url):
                    urls.append(url)
        # No repetition of same URL
        urls = list(dict.fromkeys(urls))
        return urls
    
    def start_scraping(self):
        # Start the queue of URL with the website homepage body URLs
        self._queue = self._homepage_urls
        # Initialize the database
        self.listed_url  = dict.fromkeys(self._homepage_urls,1)
        n_scraped = 1
        while len(self._queue)>0:
            sys.stdout.write("\r Number of webpages scraped: {0}/{1}".format(n_scraped,len(self.listed_url)))
            sys.stdout.flush()
            url = self._queue.pop(0)
            # Get all the unique URLs of the page
            page_urls = self.scrape_page(url)
            # All the (url, urls_list) couple to the dict
            self.urls_network[url] = page_urls
            # Add the URLs to the dict and get the list of the new
            # URLs the algorithm never saw
            new_urls = self.add_listed_url(page_urls)
            # Add the new URLs to the list of URLs pages to be scraped
            self._queue.extend(new_urls)
            n_scraped += 1
            
    def scrape_page(self, URL:str)->List[str]:
        # Request the page
        page = requests.get(URL)
        # Parse the HTML
        html = bs(page.text, 'html.parser')
        # Summarize the text
        if self.llm:
            if self.llm_kind == 'summarizer':
                self.llm_response[URL] = self.summarize_data(html)
            elif self.llm_kind == 'seo_optimizer':
                self.llm_response[URL] = self.seo_optimize(html)
        return self.get_all_urls(html)
    
    def add_listed_url(self, url_list:List[str])->List[str]:
        new_urls = []
        for url in url_list:
            if url in self.listed_url:
                self.listed_url[url] += 1
            else:
                self.listed_url[url] = 1
                new_urls.append(url)
        return new_urls
    
    def save_results(self):
        #website_name = re.search(r"//([^\.]+)\.", self._home_url).group(1)
        website_name = self._home_url.replace('https://','').replace('www.','').replace('/','')
        with open(website_name+'_listed_url.json', 'w') as fp:
            json.dump(self.listed_url, fp)
        with open(website_name+'_urls_network.json', 'w') as fp:
            json.dump(self.urls_network, fp)
        if self.llm:
            with open(website_name+'_llm_response.json', 'w') as fp:
                json.dump(self.llm_response, fp)
    
    def summarize_data(self, html:str)->str:
        text = html.text.replace('\n',' ').replace('\t',' ')
        #text = [a.text.split(',',1) for a in html][0]
        return self.llmSummarizer.summarize(text)
    
    def seo_optimize(self, html:str)->str:
        text = html.text.replace('\n',' ').replace('\t',' ')
        #text = [a.text.split(',',1) for a in html][0]
        return self.llmSeoOptimizer.optimize(text)
    
    def plot(self, use_saved_files:bool=False):
        if use_saved_files:
            plotter = networkPlotter(home_url=self._home_url)
        else:
            plotter = networkPlotter(network_data=self.urls_network, 
                                     network_weight=self.listed_url)
        plotter.plot()