api-kickstart
=============

Examples and libraries to get started using the Akamai {OPEN} APIs

Currently, this repository has:
* Libraries and clients for python

After cloning, get the needed libraries by doing the following:
python setup.py install --user

The easiest way to walk through the needed provisioning and authentication to get your 
credentials is under "provisioning" in the Getting started guide on our site:
https://developer.akamai.com/introduction/index.html

Copy the sample_edgerc file into ~/.edgerc on your system.  Replace the authentication items with your credentials.

To debug this library, you can turn on debugging:
python diagnostic_tools.py --verbose

The diagnostic_tools.py script will work automatically, and the diagnostic_tools_exercises.py
has some broken pieces  to play with and fix

Future libraries and clients will be developed for other languages as we can, and developers are welcome to send pull requests for examples they have created.

Contact khunter@akamai.com, dkazemi@akamai.com or open-developer@akamai.com for help, comments, suggestions.

Tweet your thoughts to @synedra, @tinysubversions
