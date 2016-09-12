Telecoupling Toolbox v0.9-alpha
===========
To install the Telecoupling Toolbox, make sure to follow all the steps specified below.


##Prerequisites
-----------
* R (>= 3.2.0)
* Python 2.7.x (32- and/or 64-bit)
* ArcGIS (>= 10.3. Not yet tested for 10.2 or 10.4)


##Locate Python and add it to your system PATH
------------
If you have never done this, you can check the [blog post](https://pythongisandstuff.wordpress.com/2013/07/10/locating-python-adding-to-path-and-accessing-arcpy/) on how to accomplish this. Although this step is *NOT* mandatory to follow the next steps, we **STRONGLY** recommend it to avoid having to copy/paste the full path to your python installation every time you want to open Python from command line or install any Python libraries using a package manager.


##Install Python library dependencies
---------------------
These are needed to run any tool that uses InVEST 3.3.1 models, thus it is NOT a toolbox requirement but rather an InVEST-specific requirement. You can help yourself with the [PyPI page](https://pypi.python.org/pypi/natcap.invest/3.3.1 ) for the natcap.invest package or the [InVEST API documentation](http://invest.readthedocs.io/en/latest/installing.html). Your Windows version should come with a C/C++ compiler installed and configured for your system. However, you can always download and installed the correct compiler for Python 2.7 from the [Microsoft webpage](https://www.microsoft.com/en-us/download/details.aspx?id=44266). The python [wiki page](https://wiki.python.org/moin/WindowsCompilers) on compilation under Windows can also be of help.

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

##Install the R-ArcGIS tools
---------------------

ArcGIS has developed a nice [Github webpage](https://github.com/R-ArcGIS/r-bridge-install) with lots of useful documentation on how to install a set of libraries to make sure R and ArcGIS can talk to each other.

Inside the .zip folder of the toolbox you will find another .zip folder called *r-bridge-install-master*. As the instructions in the webpage above point out, unzip the folder and open ArcMap. Go to the toolboxes menu, right-click and select to "add toolbox". Then, find the **R Integration.pyt** toolbox inside the unzipped folder and you should see a new toolbox appearing in the list of existing ones. At this point, follow the instructions from the github webpage above to make sure you have the correct R software version installed and install the appropriate libraries that ArcGIS and R need to talk to each other.

##Add the Telecoupling Toolbox to ArcGIS
---------------------

We are almost done. At this point, you are ready to add the Telecoupling Toolbox that came with the .zip folder. Follow the same procedure at step (3) to add this new toolbox to the list inside ArcMap. If all goes well, you should see it appearing in the list. Feel free to expand the 5 toolsets (*__agents__*, *__causes__*, *__effects__*, *__flows__*, *__systems__*) and find the python tool scripts inside each one of them. To learn more about the geoprocessing and mapping tasks for each one of the tool scripts, please read the documentation attached to each tool. You can either use ArcCatalog to read about description of purpose and parameters of each tool, OR you can double-click each tool inside ArcMap and read the main description found in the 'help' tab opened on the right of the user interface for the tool.

##Test the tools using the sample data provided
---------------------

You can start testing and using each tool inside the **Telecoupling Toolbox** with the set of sample data provided inside the .zip folder. There you will see a mix of GIS (vector, raster) data and tables (.csv) needed by the tools.