Telecoupling Toolbox v1.0-alpha
===========
To install the Telecoupling Toolbox, make sure to follow all the steps specified below.


## Prerequisites
-----------
* R (>= 3.2.0)
* Python 2.7.x (32- and/or 64-bit)
* ArcGIS (>= 10.3. Not yet tested for 10.2 or 10.4)


## Locate Python and add it to your system PATH
------------
If you have never done this, you can check the [blog post](https://pythongisandstuff.wordpress.com/2013/07/10/locating-python-adding-to-path-and-accessing-arcpy/) on how to accomplish this. Although this step is *NOT* mandatory to follow the next steps, we **STRONGLY** recommend it to avoid having to copy/paste the full path to your python installation every time you want to open Python from command line or install any Python libraries using a package manager.


## Install Python library dependencies
---------------------
The Telecoupling Toolbox (v1.0a) relies on a number of external software libraries that need to be installed prior to running any script tools. 

At present, these libraries include Python and R modules. Most of the Python libraries you will install are necessary to run any script tool that makes use of the [NatCap InVEST software](http://www.naturalcapitalproject.org/invest/). Therefore, these libraries are required by InVEST itself, not the Telecoupling Toolbox. You can help yourself with the [PyPI page](https://pypi.python.org/pypi/natcap.invest/3.3.1 ) for the natcap.invest package or the [InVEST API documentation](http://invest.readthedocs.io/en/latest/installing.html). Your Windows version should come with a C/C++ compiler installed and configured for your system. However, you can always download and installed the correct compiler for Python 2.7 from the [Microsoft webpage](https://www.microsoft.com/en-us/download/details.aspx?id=44266). The python [wiki page](https://wiki.python.org/moin/WindowsCompilers) on compilation under Windows can also be of help.

After installing the C/C++ compiler, you can start installing all the necessary python libraries. If you are not too familiar with Python, you may find yourself lost in installing libraries. The easiest way out is to use a "package manager", such as __*pip*__. If you have ArcGIS >= 10.4 installed on your system, the Python distribution should already come with *pip* installed (among other libraries such as *SciPy*). If you have ArcGIS < 10.4, then you should make sure to install *pip* manually, following [these directions](https://pip.pypa.io/en/stable/installing/). 

**NOTE**: *Make sure to always install Python libraries (including *pip*) that correspond to your main version (e.g. 2.7) and your 32- or 64- bit infrastructure*.

Once you installed *pip* you can start using it to install all Python libraries needed for InVEST to run:

* gdal>=1.11.2,<2.0
* matplotlib
* natcap.versioner>=0.4.2
* numpy>=1.11.0
* pyamg>=2.2.1
* pygeoprocessing>=0.3.0a17
* rtree>=0.8.2
* scipy>=0.16.1
* shapely
* setuptools>=8.0

**NOTE**: *you __MUST__ to install all the above packages prior to install the natcap.invest python library*

Open the CMD prompt on Windows and use the command **pip install** (assuming Python has been added to the PATH system variable) followed by the name of the library of interest.

**Example**:

```
pip install numpy
```

If your Python version already has a package listed above, it will automatically uninstall the old version and install the most current one. However, you want to make sure that the library version you are installing fits the minimum requirements for InVEST (see above). Otherwise, something may not work properly. You will notice that some packages, such as GDAL, are hard to install even using
'pip install'. In this or any other case the package installation goes wrong, we recommend using the Christoph Gohlke [unofficial Windows binaries](http://www.lfd.uci.edu/~gohlke/pythonlibs/) for Python packages. Binaries with .whl extension (wheels) are pre-packaged versions of python libraries. The way to install .whl binaries is to use _pip install pathtofileondisk.whl_.

**NOTE**: *The GDAL version currently found on Christoph Gohkle page is >= 2.0, which is NOT OK for InVEST. Instead, please use the .whl file found inside the folder 'pkg' that comes with the .zip of the toolbox.*

To double check you successfully installed a certain library, you can always type 'python' in your CMD prompt to start Python from command line, and type _import nameofyourpackage_, then *nameofyourpackage.\__version__*

**Example**:

```python
import numpy
numpy.__version__
```

There are no .whl (wheels) versions for either *natcap.invest* or *pygeoprocessing*. For these two, please try using *pip install*.

**Example**:

```
pip install natcap.invest
```

After you are done installing all Python libraries needed to use InVEST models, make sure to install these additional ones:

* bs4 
* BeautifulSoup 

## Install the R-ArcGIS tools 
---------------------

ArcGIS has developed a nice [Github webpage](https://github.com/R-ArcGIS/r-bridge-install) with lots of useful documentation on how to install a set of libraries to make sure R and ArcGIS can talk to each other.

Inside the .zip folder of the toolbox you will find another .zip folder called *r-bridge-install-master*. As the instructions in the webpage above point out, unzip the folder and open ArcMap. Go to the toolboxes menu, right-click and select to "add toolbox". Then, find the **R Integration.pyt** toolbox inside the unzipped folder and you should see a new toolbox appearing in the list of existing ones. At this point, follow the instructions from the github webpage above to make sure you have the correct R software version installed and install the appropriate libraries that ArcGIS and R need to talk to each other.

## Add the Telecoupling Toolbox to ArcGIS
---------------------

You are almost done! 

On the home page of the Telecoupling Toolbox repository, find the [Downloads](https://bitbucket.org/f-tonini/telecoupling-geoapp/downloads) menu on the left. Click on 'Download repository' and save the .zip file on your local computer. The zipped folder contains a snapshot of ALL current files and documents that are found in this repository. After unzipping the file, you will notice an ArcMap file (.mxd) called **TelecouplingApplication.mxd**. If you double-click on it, your ArcGIS will open and show a set of GIS layers used by the application as a basemap. Moreover, if you open the ArcToolbox tab, you should see the current version of the Telecoupling Toolbox already added to the list. Alternatively, you can open a brand new ArcMap document and follow the same procedure shown in the 'Install the R-ArcGIS tools' section to add the Telecoupling Toolbox. 

Inside the Telecoupling Toolbox you should see 5 toolsets (*__agents__*, *__causes__*, *__effects__*, *__flows__*, *__systems__*) and a number of python tool scripts inside each one of them. To learn more about what each tool script does and what parameters it takes, please refer to the help documentation that comes with it. To do so, you can either use ArcCatalog, clicking on the 'description' tab for a tool or, alternatively, click on the 'show help' button found at the bottom of each tool script after opening it (double-click on the tool script to open the user interface). 

## Test the tools using the sample data provided
---------------------

You can now start testing and using the toolbox using the set of sample data ('SampleData.zip') provided with this repository. After unzipping the sample data folder, you will see a mix of GIS (vector, raster) data and tables (.csv) needed as input parameters by the script tools.