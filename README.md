api-kickstart
=============

Examples and libraries to get started using the Akamai {OPEN} APIs

Currently, this repository has:
* Libraries and clients for python

## Installation
After cloning, get the needed libraries by doing the following from the examples/python directory:
```bash
$ git clone https://github.com/akamai-open/api-kickstart.git
$ python tools/setup.py install --user
```

## Installation support
If you have issues with the setup command, check the following link:
http://stackoverflow.com/questions/4495120/combine-user-with-prefix-error-with-setup-py-install

## How To
The easiest way to walk through the needed provisioning and authentication to get your credentials is under "provisioning" in the Getting started guide on our site:
https://developer.akamai.com/introduction/index.html

### Credentials
You can get your credentials set up by using the gen_edgerc.py command in the examples/python directory:
```bash
$ python gen_edgerc.py
``` 

## Example: Diagnostic tools
For examples other than diagnostic_tools you'll want to pass the name of the appropriate section as an
argument, for example this is how you'd set up ccu.py:
```bash
python gen_edgerc.py ccu
python ccu.py
```

## Debugging
To debug this library, you can turn on debugging:
```bash
python diagnostic_tools.py --verbose
```

The diagnostic_tools.py script will work automatically, and the diagnostic_tools_exercises.py has some broken pieces to play with and fix

Future libraries and clients will be developed for other languages as we can, and developers are welcome to send pull requests for examples they have created.

## Further examples
Some more complete applications have been placed into the /apps subdirectory, and they can be retrieved using Git submodules:
```bash
$ git submodule init
$ git submodule update
```
Each has a README explaining what it is and how it works.

## Authors & Feedback
Contact khunter@akamai.com open-developer@akamai.com for help, comments, suggestions.

Tweet your thoughts to @synedra
