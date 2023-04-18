My reworking and fixes
===============

- Rebase of the project into one main folder, adandoning pyfpdb folder which can cause ugly bugs when packaging especially under Windows
- Fix of importing issue on some poker sites
- Fix of graph tourney viewer with other currencies than dollars
- Fix of log viewer
- Fix of minor bugs

How to install?
----

Grab the code from this git branch.  Install dependencies - I use
macports to install things on mac.

I _believe_ these are the required packages:

py27-matplotlib, py27-pyqt5, py27-pyobjc-quartz.

A couple of the HH parsers (Merge and Winamax) require
py27-BeautifulSoup.  I have not installed this package or tested those
parsers.

Macports should install everything else you need automagically.

Users on other platforms don't need the pyobjc stuff.

If you want all-in EV calculation, you'll also want pokereval and
pypokereval.  I had to build pypokereval myself to add python 2.7
support, so if you can't be bothered with that you'll want to
substitute the py26 versions of the above.

Next you'll have to run `sudo port select --set python python27` and
possibly `hash -r` in case your shell has the system python command
cached.

Now you should be able to start fpdb like this:
`./run_fpdb.py`

## Windows

To install from source follow procedure on wiki: http://fpdb.wikidot.com/developer:run-new

- For HUD using GTK you need to install my GTK2 runtime version (GTK-2.22.1-runtime.zip) from windows packaging folder and add its bin folder (e.g. C:\GTK\bin) to environment PATH, and install unofficial PyGTK modules for Py2.7x64 from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygtk
- To use PokerEval you need to install my compiled PyPoker-Eval module for Py2.7x64 from windows packaging folder (pypoker-eval-x64)
- I also provide on my Releases an already FPDB-x64 compiled distribution and a Windows Installer made with the free powerful InstallForge: https://installforge.net/download/
