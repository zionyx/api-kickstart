# Python edgegrid module
# Handles command line options and environment variables
# Options: 
# CLIENT_TOKEN
# CLIENT_SECRET
# HOST
# ACCESS_TOKEN
# MAX_BODY (optional)
# VERBOSE (optional)
# CONFIG_FILE (optional, defaults to ~/.edgerc, only settable via command line or env var)

import ConfigParser,os,sys
import httplib
import urllib
import urllib2
import logging
import uuid
import hashlib
import hmac
import base64
import re
import json
from time import gmtime, strftime
from urlparse import urlparse, parse_qsl, urlunparse

if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    print("This script requires Python version 2.7")
    sys.exit(1)

logger = logging.getLogger(__name__)

class EdgeGridConfig():

	def __init__(self, config_values):
		
		required_options = ['client_token','client_secret','host','access_token','path']
		optional_options = {'max_body':1024,'verbose':False, 'schema':'https'}
		arguments = {}
		for argument in required_options:
			if argument in config_values and config_values[argument]:
				arguments[argument] = config_values[argument]
				required_options.remove(argument)		
		
		# sys.argv (command line) trumps all
		for command_line_arg in sys.argv:
			if command_line_arg.startswith('--') and command_line_arg not in arguments:
				(arg,val) = command_line_arg.split('=')
				arg = arg[2:].lower()
				arguments[arg] = val

		# Environment variables are next
		for key in os.environ:
			lower_key = key.lower()
			if lower_key not in arguments and (lower_key in required_options or lower_key in optional_options):
				arguments[lower_key] = os.environ[key]

		if "config_file" not in arguments:
			arguments["config_file"] = "~/.edgerc"	
		arguments["config_file"] = os.path.expanduser(arguments["config_file"])	
	
		# The config file is actually optional,
		# so only try to parse it if it's there
		if os.path.isfile(arguments["config_file"]):
			config = ConfigParser.ConfigParser()
			config.readfp(open(arguments["config_file"]))
			for key, value in config.items("default"):
				# ConfigParser lowercases magically
				if key not in arguments:
					arguments[key] = value
				if key == 'headers':
					arguments['headers'] = {}
					for header in value.split(','):
						headkey,headvalue = header.split(':')
						arguments['headers'][headkey] = headvalue
				if key == 'testghost':
					arguments['testghost'] = value
			
		missing_args = []
		for argument in required_options:
			if argument not in arguments:
				missing_args.append(argument)

		if len(missing_args) > 0:
			print "Missing args: %s" % missing_args
			exit()

		for key in optional_options:
			lower_key = key.lower()
			if key not in arguments:
				arguments[lower_key] = optional_options[key]

		for option in arguments:
			setattr(self,option,arguments[option])

		self.create_base_url()

	def create_base_url(self):
		if "https" in self.host:
			self.base_url = self.host

		elif "luna.akamaiapis.net" in self.host:
			self.base_url = "https://%s" % self.host

		else: # They must have just put in the string
			self.base_url = "https://%s.luna.akamaiapis.net" % self.host
			
	def make_call(self, path, http_method, parameters=None, options=None):
		signer = EGSigner(
		    self.host,
                    self.client_token,
                    self.access_token,
	   	    self.client_secret,
		    self.verbose,
                    self.max_body)
		url = ''.join([self.base_url,path])
		headers = []
		data = None

		params = ''
		if parameters:
			params = urllib.urlencode(parameters)
		if parameters and http_method == 'GET':
			url = '?'.join([url,params])
			path = '?'.join([path,params])

		auth_header = signer.get_auth_header(url, http_method, headers, data)

		headers = {"Authorization": auth_header}
		httplib.HTTPConnection.debuglevel = 1
		conn = httplib.HTTPSConnection(self.host)
		conn.request(http_method, path, '', headers)
		response = conn.getresponse()
		if response.status != 200:
			print "Bad response code: %s (%s)" % (response.status, response.reason)
			return
		data = json.loads(response.read())
		return data	
		# Grab and process the options
		# Make the call
		# Grab the results and add to the object

class EGSigner(object):
  def __init__(self, host, client_token, access_token, secret, verbose, max_body, signed_headers=None):
    self.host = host
    self.client_token = client_token
    self.access_token = access_token
    self.secret = secret
    self.verbose = verbose
    self.max_body = max_body
    self.signed_headers = signed_headers

  def sign(self, data, key, algorithm):
    result = hmac.new(key, data, algorithm)
    return result.digest()

  def get_auth_header(self, url, method, headers=None, data=None):  
    timestamp = strftime("%Y%m%dT%H:%M:%S+0000", gmtime())

    request_data = self.get_request_data(url, method, headers, data)
    auth_data = self.get_auth_data(timestamp)
    request_data.append(auth_data)
    string_to_sign = '\t'.join(request_data)
    if self.verbose: print "String-to-sign: %s" %(string_to_sign)

    key_bytes = self.sign(bytes(timestamp), bytes(self.secret), hashlib.sha256)
    signing_key = base64.b64encode(key_bytes)
    signature_bytes = self.sign(bytes(string_to_sign), bytes(signing_key), hashlib.sha256)
    signature = base64.b64encode(signature_bytes)
    auth_header = '%ssignature=%s' %(auth_data, signature)
    return auth_header


  def get_auth_data(self, timestamp):
    auth_fields = []
    auth_fields.append('client_token=' + self.client_token)
    auth_fields.append('access_token=' + self.access_token)
    auth_fields.append('timestamp=' + timestamp)
    auth_fields.append('nonce=' + str(uuid.uuid4()))
    auth_fields.append('')
    auth_data = ';'.join(auth_fields)
    auth_data = 'EG1-HMAC-SHA256 ' + auth_data
    if self.verbose: print "Auth data: %s" %(auth_data)
    return auth_data


  def get_request_data(self, url, method, headers, data):
    request_data = []
    if not method:
      if data:
        method = 'POST'
      else:
        method = 'GET'
    else:
      method = method.upper()
    request_data.append(method)
    
    parsed_url = urlparse(url)
    request_data.append(parsed_url.scheme)
    request_data.append(self.host)
    request_data.append(self.get_relative_url(url))
    request_data.append(self.get_canonicalize_headers(headers))
    request_data.append(self.get_content_hash(method, data))
    return request_data

  def get_relative_url(self,url):
    relative_url = ''
    auth_index = url.find('//')
    path_index = url.find('/', auth_index+2)
    if path_index == -1:
      relative_url = '/'
    else:
      relative_url = url[path_index:]
    return relative_url


  def get_canonicalize_headers(self, headers):
    canonical_header = '' 
    headers_values = []
    if headers == None or self.signed_headers == None:
	return '' 
    if self.verbose: print self.signed_headers
    for header_name in self.signed_headers:
      header_value = ''
      if header_name in headers:
        header_value = headers[header_name]
      if header_value:
        header_value = header_value.strip()
        p = re.compile('\\s+')
        new_value = p.sub(' ', header_value) 
        canonical_header = header_name + ':' + new_value
        headers_values.append(canonical_header)
    headers_values.append('')
    canonical_header = '\t'.join(headers_values)
    if self.verbose: print "Canonicalized header: %s" %(canonical_header)
    return canonical_header

  def get_content_hash(self, method, data):
    content_hash = ''

    if method == 'POST':
        if len(data) > self.max_body:
          if self.verbose: print "Data length %s larger than maximum %s " % (len(data),self.max_body)
          data = data[0:self.max_body]
          if self.verbose: print "Data truncated to %s for computing the hash" % len(data)

        # compute the hash
        md = hashlib.sha256(data).digest()
        content_hash = base64.b64encode(md)
    return content_hash
