# Python edgegrid module
# Handles command line options and environment variables

class EdgeGridClient:
	"""The base client for edgegrid objects in python"""
	# Handle environment variables
	  # Config file (~/.akamairc)
	  # Credentials
	  # Verbosity
	# Handle command line options
	  # Command line credentials override other options, priority is:
		# Command line credentials
		# Environment variables
		# Config file
	  # Command line path option overrides other options as well

	def make_call(path, method, options):
		# Check the path for https:// and use the right piece
		# Grab and process the options
		# Set the method
		# Make the call
		# Grab the results and add to the object
