**********
* README
**********

------------------------------------------------------------------------------------------------
author: Francesco Tonini
date: 09/09/2016
purpose: installation guidelines for ESRI ArcGIS Telecoupling Toolbox v0.9-alpha (unstable) 
operative system: tested on Windows 10
software requirement: 
	* Windows 10 (not yet tested on Windows 7)
	* R (>= 3.2.0)
	* Python 2.7.x (32- and/or 64-bit)
        * ArcGIS (>= 10.3. Not yet tested for 10.2 or 10.4)
----------------------------------------------------------------------------------------------

To install the Telecoupling Toolbox, make sure to follow all the steps specified below.

1) Locate Python and add it to your system PATH environment variable: 
============================================================================
If you have never done this, you can check the following blog post on how to accomplish this:
https://pythongisandstuff.wordpress.com/2013/07/10/locating-python-adding-to-path-and-accessing-arcpy/
Although this step is not mandatory to follow the next steps, we STRONGLY recommonded to do so and avoid having to copy/paste the full path to your python installation
every time you want to open Python from command line or install any Python libraries using a package manager.

2) Install all the necessary Python library dependencies:
==================================================================== 
These are needed to run any tool that uses InVEST 3.3.1 models, thus it is NOT a toolbox requirement but rather an InVEST-specific requirement.

You can help yourself with the PyPI page for the natcap invest package: 
https://pypi.python.org/pypi/natcap.invest/3.3.1 

OR the InVEST API documentation here:
http://invest.readthedocs.io/en/latest/installing.html

Your Windows version should come with a C/C++ compiler installed and configured for your system. However, you can always download and installed the correct compiler for Python 2.7 here:
https://www.microsoft.com/en-us/download/details.aspx?id=44266

The python wiki page on compilation under Windows can also be of help:
https://wiki.python.org/moin/WindowsCompilers

After installing the C/C++ compiler, you can start installing all the necessary python libraries. If you are not too familiar with Python, you may find yourself lost in installing libraries.
The easiest way out is to use a "package manager", such as 'pip'. If you have ArcGIS >= 10.4 installed on your system, the Python distribution should already come with 'pip' installed (among other libraries such as SciPy).

If you have ArcGIS < 10.4, then you should make sure to install 'pip' manually, following these directions: 
https://pip.pypa.io/en/stable/installing/

***IMPORTANT*** 
Make sure to always install Python libraries (including pip) that correspond to your main version (e.g. 2.7) and your 32- or 64- bit infrastructure 
****************************************************************************************************************************************************

Once you installed 'pip' you can start using it to install all Python libraries needed for InVEST to run:
gdal>=1.11.2,<2.0
matplotlib
natcap.versioner>=0.4.2
numpy>=1.11.0
pyamg>=2.2.1
pygeoprocessing>=0.3.0a17
rtree>=0.8.2
scipy>=0.16.1
shapely
setuptools>=8.0

**NOTE: you MUST to install all the above packages prior to install the natcap.invest python library (as pointed out in the PyPI page above)**

Open the CMD prompt on Windows and type (assuming Python has been added to the PATH system variable):
pip install name_of_your_package
---------------
Example:
pip install numpy

If your Python version already has a package listed above, it will automatically uninstall the old version and install the most current one. However, you want to make sure that the library version
you are installing fits the minimum requirements for InVEST (see above). Otherwise, something may not work properly. You will notice that some packages, such as GDAL, are hard to install even using
'pip install'. In this or any other case the package installation goes wrong, we recommend using the Christph Gohlke unofficial Windows binaries for Python packages:
http://www.lfd.uci.edu/~gohlke/pythonlibs/. Binaries with .whl extension (wheels) are pre-packaged versions of python libraries. The way to install .whl binaries is to use 'pip install path_to_file_on_disk.whl'.

***IMPORTANT***
The GDAL version currently found on Christoph Gohkle page is >= 2.0, which is NOT OK for InVEST. Instead, please use the .whl file found inside the folder 'pkg' that comes with the .zip of the toolbox.
************************************************************************************************************************************************************************************************

To double check you successfully installed a certain library, you can always type 'python' in your CMD prompt to start Python from command line, and type
'import name_of_your_package', then 'name_of_your_package.__version__'
-------------------
Example:
import numpy
numpy.__version__

There are no .whl (wheels) versions for either natcap.invest or pygeoprocessing. For these two, please try using 'pip install'.
----------------
Example:
pip install natcap.invest


3) Install the R-ArcGIS tools:
=====================================

ArcGIS has developed a nice Github webpage with lots of useful documentation on how to install a set of libraries to make sure R and ArcGIS can talk to each other:
https://github.com/R-ArcGIS/r-bridge-install

Inside the .zip folder of the toolbox you will find another .zip folder called 'r-bridge-install-master'. As the instructions in the webpage above point out, unzip the folder and open ArcMap. 
Go to the toolboxes menu, right-click and select to "add toolbox". Then, find the R Integration.pyt toolbox inside the unzipped folder and you should see a new toolbox appearing in the list of existing ones.
At this point, follow the instructions from the github webpage above to make sure you have the correct R software version installed and install the appropriate libraries that ArcGIS and R need to talk to each other.

4) Add the Telecoupling Toolbox to ArcGIS:
==============================================

We are almost done. At this point, you are ready to add the Telecoupling Toolbox that came with the .zip folder. Follow the same procedure at step (3) to add this new toolbox to the list inside ArcMap.
If all goes well, you should see it appearing in the list. Feel free to expand the 5 toolsets (agents, causes, effects, flows, systems) and find the python tool scripts inside each one of them.
To learn more about the geoprocessing and mapping tasks for each one of the tool scripts, please read the documentation attached to each tool. You can either use ArcCatalog to read about description of purpose
and parameters of each tool, OR you can double-click each tool inside ArcMap and read the main description found in the 'help' tab opened on the right of the user interface for the tool.

5) Test the tools using the sample data provided:
=====================================================
You can start testing and using each tool inside the Telecoupling Toolbox with the set of sample data provided inside the .zip folder. There you will see a mix of GIS (vector, raster) data and tables (.csv) needed
by the tools.






