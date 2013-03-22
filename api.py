"""
This module provides an oo wrapper around eBay's V1 API for use in Python projects or easy-access via terminal
"""
import httplib2
import base64
import simplejson as json
from httplib2 import socks
import urllib2
import urllib

API_HOST = "http://svcs.ebay.com"
API_PATH = "/services/search/FindingService/v1"
APP_ID = "insertappIDhere"
GLOBAL_ID = "0"
SERVICE_VERSION = "1.0.0"
DATA_FORMAT = "JSON"
HTTP_PROXY = None
HTTP_PROXY_PORT = 80

class Connection(object):
    host = API_HOST
    base_path = API_PATH
    app_id = APP_ID
    global_id = GLOBAL_ID
    data_format = DATA_FORMAT
    version = SERVICE_VERSION
    http_proxy = HTTP_PROXY
    http_proxy_port = HTTP_PROXY_PORT
	
    
	    
    def request_json(self, method, operation, service=None, data=None):
    	response = self.request(method, operation, service, data)
        if response.getcode() == 200 or response.getcode() == 201:
            return json.loads(response.read())  
        else:
            raise Exception(response)
	
    def request_headers(self, operation):
        return {
		'X-EBAY-SOA-SECURITY-APPNAME'  : self.app_id,
		'X-EBAY-SOA-VERSION': self.version,
         'X-EBAY-SOA-OPERATION-NAME' : operation,
         'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON'
            }
            
    def request(self, method, operation, service=None, data=None):
        url = self.host + self.base_path
        headers = self.request_headers(operation)
        
        if data:
            headers = self.request_headers(operation)
            headers['X-EBAY-SOA-SERVICE-NAME'] = service
            headers['X-EBAY-SOA-REQUEST-DATA-FORMAT'] = 'JSON'
            
        request = urllib2.Request(url)
        for key, value in headers.items():
            request.add_header(key, value) 
            
        try:
            return urllib2.urlopen(request, data)
        except urllib2.HTTPError, error:
            raise Exception(error.read(), request.headers)
	
		
class Search(object):
    """Base methods & attributes"""
    client = Connection()
	
    def __init__(self):
        pass
		
    def __iter__(self):
        return self

    def next(self):
        self.current_page = self.current_page + 1
        resource_list = self.get(self.query)
        
        if not resource_list:
            raise StopIteration
        else:
            return resource_list
            
class ServiceUp(Search):
    """Returns eBay Version but more importantly let's user know server is running"""
    operation = "getVersion"
    def get(self):
        result = self.client.request_json('POST', self.operation)
        return result
    
class Finding(Search):
    """Utilizes eBay Finding API to return JSON-formatted product searches"""
    service = 'FindingService'
    modes = ['getSearchKeywordsRecommendation', 'findItemsByKeywords', 'findItemsByKeywords'
	         'findItemsByCategory', 'findItemsAdvanced', 'findItemsByProduct', 'findItemsIneBayStores', 'getHistograms']
	
    """Default pagination set and operation for easy running"""
    def __init__(self, pagination=20, current_page=1):
        self.paginate_by = pagination
        self.page = current_page
        self.operation = "findItemsByKeywords"
	
    """Sets modes for Finding APIs"""
    def set_mode(self, modeInt):
        self.operation = self.modes[modeInt]
	
    """
    Main method for returning JSON
    TODO: json_body is unreadable even to me.
    """
    def get(self, query):
        self.query = query
        json_body = json.loads(json.dumps('{"jsonns.xsi":"http://www.w3.org/2001/XMLSchema-instance","jsonns.xs":"http://www.w3.org/2001/XMLSchema","jsonns.tns":"http://www.ebay.com/marketplace/search/v1/services","tns.findItemsByKeywordsRequest":{"keywords":"%s", "paginationInput":{"pagination.pageNumber": "%s","paginationInput.entriesPerPage":"%s"}}}' % (query, self.page, self.paginate_by)))
        item_list = self.client.request_json('POST', self.operation, self.service, json_body)
        return item_list
		
		
class Buying(Search):
    """Utilizes eBay Shopping API to return JSON-formatted data about specific products"""
    pass
