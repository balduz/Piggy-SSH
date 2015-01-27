# Piggy-SSH
Piggy SSH is a plugin for Sublime Text 3 that allows an Apache Pig developer to run a script against a cluster by sending the script through SSH. All the logs and the output generated are printed to the ST3 console. To avoid sending too many requests by accident to a cluster, it is currently limited to one only job at a time. Any attempt to send a second job will show the user a dialog asking wether he wants to cancel the previous job in order to send the new one.

![Piggy SSH Example](http://balduz.github.io/piggy-ssh-example.PNG)

#### Installation
To connect via SSH, this plugin needs the Python library paramiko, which also requires pycrypto and ecdsa.

- First of all, download the plugin from [GitHub](https://github.com/balduz/Piggy-SSH/archive/master.zip) and unzip it into your Packages folder. If you don't know where this folder is, go to `Sublime Text -> Preferences -> Browse Packages...`.

* Sublime Text 3 uses Python 3.3, and the only way to get [pycrypto](https://pypi.python.org/pypi/pycrypto) for Python 3.3 right now is to download the prebuild binaries from [here.](http://www.voidspace.org.uk/python/modules.shtml#pycrypto) You will need Python 3.3 (not the one from ST3, a different installation), so that the executable is installed, otherwise it won't find where it needs to be installed. Now, grab the Crypto folder from `path_to_python/lib/site-packages` and paste it in the ST3 packages folder, just like you did with PiggySSH.

* As for [ecdsa](https://pypi.python.org/pypi/ecdsa), just grab a terminal and type `pip install ecdsa`, and then again paste the ecdsa folder from *path_to_python/lib/site-packages* to your Packages folder.

* Finally, you need the [paramiko](http://www.paramiko.org/) module, but the one installed by pip has some relative import issues when using it in Sublime Text 3, so grab a modified one [here](http://balduz.github.io/paramiko.zip) and unzip it again in the Packages folder.

Now, you should have the following structure:

1. a
2. b
c
d
e

