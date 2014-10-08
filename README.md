api-kickstart
=============

Examples and libraries to get started using the Akamai {OPEN} APIs

Currently, this repository has:
* Libraries and clients for python

In order to install this at this point, you will need to install the Python OpenEdge client.  
The easiest way to walk through the needed provisioning and authentication to get your credentials
is to visit our getting started guide on our website here:
https://developer.akamai.com/introduction/index.html

To debug this library, you can turn on debugging in the following ways:
python diagnostic_tools.py --verbose=True
export AKAM_VERBOSE=True
Add the following to your .edgerc file under the server you're using (default for the main script): verbose = True

During the bootcamp where this was initially released, there were authentication errors added to the
configuration file, and you need to create an .edgerc file in your home directory in order to use
this library.  Copy the sample_edgerc file to a file (not a directory) named .edgerc in your home 
directory.  You can the your credentials that you get from the above exercise into the section
marked "default" at the top.  Leave the "broken" section as it is and fix each piece as you encounter
the issues - so you can become familiar with what our various error messages look like.

The diagnostic_tools.py script will work automatically, and the diagnostic_tools_exercises.py
has some broken pieces along with the authentication errors you'll be fixing first.

Future libraries and clients will be developed for other languages as we can, and developers are welcome to send pull requests
for examples they have created.
