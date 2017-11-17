Telecoupling Toolbox: ArcGIS Toolbox v1.3b
========================

## Major Releases
------------------
* Version 1.3 (_beta_)

This release adds a new tool within the Socieconomic Analysis toolset, called _Nutrition Metrics_, a custom tool that estimates the population within an Area of Interest (AOI) by age groups and then calculates the Lower Limit of Energy Requirement (LLER; in kilocalories / day) for age groups within the AOI. _NOTE: This tool will only run with Areas of Interest in Africa, Asia, or South America / Central America / Caribbean._

* Version 1.2 (_beta_)

This release adds a new tool within the Socieconomic Analysis toolset, called _Population Count and Density_, a modified version of the Population Density Metrics tool from the Analytical Tools Interface for Landscape Assessments (ATtILA) by the United States Environmental Protection Agency (EPA).

* Version 1.1 (_beta_)

This release adds two new tools, the _Habitat Risk Assessment Preprocessor_ and the _Habitat Risk Assessment_, both customized from InVEST (3.3.3). Sample data is now shipped separately from the main code repository to reduce its size. The main toolbox file (.tbx) has been updated to reflect the change in version and development stage as well as naming convention (Telecoupling _Toolbox_ instead of _Tools_). The old ‘Effect’ toolset has now been partitioned into two new toolsets: Environmental Analysis and Socioeconomic Analysis. 

* Version 1.0 (_beta_)

This version moves the development stage from _alpha_ to _beta_ after several months of testing. Some tools might still return errors or have bugs in it, but testing was successful on several different machines and settings. This version updates the InVEST tools to version __3.3.3__ and its dependencies such as the PyGeoprocessing library (_updated to version 0.3.2_). All .bat files inside the PyLibs folder have been updated to reflect this change. The main toolbox file (.tbx) has been updated to reflect the change in version and development stage.

* Version 1.2 (_alpha_)

This release eliminates the redundant presence of the “Draw Radial Flows and Nodes” tool (Flows toolset) while incorporating its old functionality into the existing “Draw Radial Flows” tool. 
The latter can now optionally draw and additional layer on top of the default flow lines, showing nodes at each flow destination, which can then be symbolized according to an attribute (quantity) of interest. 
The toolbox is still in _alpha_ development stage and is being tested for bugs and errors that need to be addressed before releasing a more stable _beta_ version.

* Version 1.1 (_alpha_)

This release includes an upgrade in the CO2 emission script tool accounting for number of wildlife units transferred and transportation capacity of the medium used. 
The tool now allows testing of future CO2 emission scenarios for wildlife transfer compared to current conditions.
The toolbox is still in _alpha_ development stage and is being tested for bugs and errors that need to be addressed before releasing a more stable _beta_ version.

* Version 1.0 (_alpha_)

This is the first version officially released for the Telecoupling Toolbox for ArcGIS. 
The toolbox is still in _alpha_ development stage and is being tested for bugs and errors that need to be addressed before releasing a more stable _beta_ version.

## Minor Releases
------------------
* Version 1.2.1 (_alpha_)

Fixed bug in the Habitat Quality tool (Effects toolset) potentially producing negative values for habitat quality and degradation output rasters.

* Version 1.1.1 (_alpha_)

Added output layer name fields in the Cost-Benefit Analysis (Wildlife Transfer) and Draw Radial Flows tools.

* Version 1.0.1 (_alpha_)

Fixed bug in the script tools linked to InVEST (3.3.1) that caused any output vector and raster files to incorrectly align with the input layers. The issue seems to be caused by the way ArcGIS interprets the spatial reference (projection string) of output files saved by the InVEST software. 
A workaround has been implemented, automatically re-defining the projection of the output layers before showing in the table of content in ArcGIS.

## Prerequisites
-----------

To install the Telecoupling Toolbox for ArcGIS, make sure to follow all the steps specified below.

* [R (3.2.0 or later)](https://www.r-project.org/)
* ArcGIS (10.3.1 or later)
* Python 2.7.x **(ArcGIS comes with Python, so no need to install a standalone version of Python!)**

**_NOTE: versions of ArcGIS prior to 10.3.1 may still work with some of our tools but have NOT been tested. ArcGIS Pro has also NOT been tested yet! Python 2.7.x ships together with ArcGIS and is automatically installed with it. If possible, avoid installing multiple versions of Python on your system as it may create conflicts and errors. If you are using Anaconda, you may need additional settings to make sure you can run the tools smoothly. For more info, check [this website](https://pymorton.wordpress.com/2014/06/17/using-arcpy-with-anaconda/)._**)

## Install Python libraries for 3rd party external software
---------------------
The Telecoupling Toolbox for ArcGIS relies on a number of python libraries that are required to run tools that use external software (e.g. InVEST). If you skip this step, tools using any external software will NOT work. 

1. Although your computer may already have a C++ compiler installed, follow this step and **Download** and **install** the [Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
2. Follow the instructions below depending on the version of ArcGIS installed on your system:
    * **ArcGIS 10.3.1 (standard 32-bit version)**: 
        * Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and save it on a local folder
        * Open the CMD prompt on Windows and type:
        `C:\Python27\ArcGIS10.3\python.exe` followed by the **full path** to `get-pip.py` (*for example if you downloaded and saved the file on your D:\ drive, the full path would be ``D:\get-pip.py``*)
        * Hit _Enter_ to run the command above
		* Make sure `pip` is installed and upgraded to latest version by running the command 
		`C:\Python27\ArcGIS10.3\python.exe -m pip install -U pip`
        * Open the folder `PyLibs` found inside the (unzipped) ArcGIS Toolbox folder
        * Double-click on the `ArcGIS103_Py32_libs.bat` file
        * If you get errors that prevent installation of any of the required packages, please contact us with detailed information
    * **ArcGIS 10.4.x (standard 32-bit version)**: 
	    * Open the CMD prompt on Windows and make sure the Python package manager `pip` is installed and upgraded to latest version by running the command 
		`C:\Python27\ArcGIS10.4\python.exe -m pip install -U pip`
        * Open the folder `PyLibs` found inside the (unzipped) telecoupling project folder
        * Double-click on the `ArcGIS104_Py32_libs.bat` file
    * **ArcGIS 10.5.x (standard 32-bit version)**: 
		* Open the CMD prompt on Windows and make sure the Python package manager `pip` is installed and upgraded to latest version by running the command 
		`C:\Python27\ArcGIS10.5\python.exe -m pip install -U pip`
        * Open the folder `PyLibs` found inside the (unzipped) telecoupling project folder
        * Double-click on the `ArcGIS105_Py32_libs.bat` file

## Install the R-ArcGIS Bridge (*this step does NOT depend on the previous section and can be completed separately!*)
---------------------

In order to allow interaction between ArcGIS and the R software, you will need to follow the next few steps:

* Open ArcMap (**NOTE: make sure you have admin rights on your computer or the next steps will not work!**)
* Find and open the Geoprocessing ArcToolbox window (Menu > Geoprocessing > ArcToolbox) 

![Figure 1](Figs/ex1.png)

* Right-click the ArcToolbox folder and select "Add Toolbox..."

![Figure 2](Figs/ex2.png)

* Browse to the `r-bridge-install-master` folder found inside the unzipped telecoupling project folder and select the `R Integration.pyt` toolbox

![Figure 3](Figs/ex3.png)

* After the toolbox has been added to the ArcToolbox list, click on it to open it and double-click on the `Install R Bindings` tool to open its interface. Click on OK to run it.  

![Figure 4](Figs/ex4.png)

If you need more details and information, ESRI has developed a nice [Github webpage](https://github.com/R-ArcGIS/r-bridge-install) with lots of useful documentation on how to install a set of libraries to make sure R and ArcGIS can talk to each other.

## Add the Telecoupling Toolbox to ArcGIS
-------------------------------------------

You are almost done! Now that you installed all Python 3rd party libraries and the R-ArcGIS Bridge, you are ready to use and test the **Telecoupling Toolbox for ArcGIS**. 

Follow these steps to add the Toolbox to your ArcMap document:

1. Open ArcMap
2. Right-click on the ArcToolbox folder and select "Add Toolbox"
3. Browse to the unzipped ArcGIS Toolbox folder and select `Telecoupling Toolbox v1.3b.tbx`

Inside the Telecoupling Toolbox you should see 5 toolsets (*__agents__*, *__causes__*, *__environmental analysis__*, *__socioeconomic analysis__*, *__flows__*, *__systems__*) and a number of python tool scripts inside each one of them. 

![Figure 5](Figs/ex5.png)

To learn more about what each tool script does and what parameters it takes, please refer to the user guide found inside the `Documentation` folder. Alternatively, each tool will have a help window associated with it explaining what each parameter is and a general description of the tool. To open the help window, click on the 'show help' button found at the bottom of each tool script after opening it (double-click on the tool script to open the user interface).

![Figure 6](Figs/ex6.png)
![Figure 7](Figs/ex7.png)

That's it! The Telecoupling Toolbox is now added to the ArcToolbox list and you can start using it with the set of [sample data](https://s3.amazonaws.com/telecoupling-toolbox-sample-data/SampleData_ArcGIS_v1.3b.zip)
After unzipping the sample data folder, you will see a mix of GIS (vector, raster) data and tables (.csv) needed as input parameters by the script tools.

## Credits and Contacts
---------------------

© 2017 Michigan State University 

Francesco Tonini: <ftonini84@gmail.com>

Paul McCord: <paulfmccord@gmail.com>

Jianguo 'Jack' Liu: <liuji@anr.msu.edu>

## LICENSE
---------------------

Telecoupling Toolbox (“Software”) is the property of Michigan State University (“MSU”) and is made available solely for educational or non-commercial use. See [LICENSE](LICENSE) for details.


* This toolbox depends on the R Statistical Computing Software:

© 2017 The [R Foundation for Statistical Computing](https://www.r-project.org/). R is free software and comes with ABSOLUTELY NO WARRANTY. See the [COPYRIGHTS](https://github.com/wch/r-source/blob/trunk/doc/COPYRIGHTS) file for details.

* This toolbox depends on [ESRI software](www.esri.com):

© 2017 ESRI. See the [Software License and Agreement](http://www.esri.com/legal/software-license) for details.

* This toolbox depends on [InVEST - Natural Capital Project software](http://www.naturalcapitalproject.org/invest/):

© 2017 NatCap Project. See the [Software License and Agreement](https://pypi.python.org/pypi/natcap.invest/3.3.1) for details.
