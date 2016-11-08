Telecoupling Toolbox v1.1.1a
===========

## Major Releases
------------------
* Version 1.1 (_alpha_)

This release includes an upgrade in the CO2 emission script tool accounting for number of wildlife units transferred and transportation capacity of the medium used. 
The toolbox is still in alpha development stage and is being tested for bugs and errors that need to be addressed before releasing a more stable beta version.

* Version 1.0 (_alpha_)

This is the first version officially released for the Telecoupling Toolbox for ArcGIS. 
The toolbox is still in _alpha_ development stage and is being tested for bugs and errors that need to be addressed before releasing a more stable _beta_ version.

## Minor Releases
------------------

* Version 1.0.1 (_alpha_)

Fixed bug in the script tools linked to InVEST (3.3.1) that caused any output vector and raster files to incorrectly align with the input layers. The issue seems to be caused by the way ArcGIS interprets the spatial reference (projection string) of output files saved by the InVEST software. 
A workaround has been implemented, automatically re-defining the projection of the output layers before showing in the table of content in ArcGIS

## Prerequisites
-----------

To install the Telecoupling Toolbox, make sure to follow all the steps specified below.

* R (3.2.0 or later)
* ArcGIS (10.3.1 or later)
* Python 2.7.x (**do NOT install a standalone version of Python! This is installed automatically with ArcGIS**)

## Download and unzip the Telecoupling Toolbox repository
---------------------
1. Find the [Downloads](https://bitbucket.org/f-tonini/telecoupling-geoapp/downloads) menu on the left of the main overview page. 
2. Click on 'Download repository' and save the .zip file on your local computer. 
3. Unzip the folder and take a look at the file content and structure. The zipped folder contains a snapshot of ALL current files and documents that are found in this repository. 

## Install Python libraries for 3rd party external software
---------------------
The Telecoupling Toolbox relies on a number of python libraries that are required to run tools that use external software (e.g. InVEST). If you skip this step, tools using any external software will NOT work. 

1. Download and install the [Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
2. Follow the instructions below depending on the version of ArcGIS installed on your system:
    * **ArcGIS 10.3.1 (standard 32-bit version)**: 
        * Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
        * Open the CMD prompt on Windows and type:
        `C:\Python27\ArcGIS10.3\python.exe` followed by the full path to `get-pip.py` downloaded file
        * Hit _Enter_ to run the command above
        * Open the folder `PyLibs\32bit` found inside the (unzipped) telecoupling toolbox folder
        * Double-click on the `ArcGIS103_Py32_libs.bat` file
    * **ArcGIS 10.3.1 (with 64-bit Background Geoprocessing)**: 
        * Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
        * Open the CMD prompt on Windows and type:
        `C:\Python27\ArcGISx6410.3\python.exe` followed by the full path to `get-pip.py` downloaded file
        * Hit _Enter_ to run the command above
        * Open the folder `PyLibs\64bit` found inside the (unzipped) telecoupling toolbox folder
        * Double-click on the `ArcGISx64103_Py64_libs.bat` file
    * **ArcGIS 10.4.x (standard 32-bit version)**: 
        * Open the folder `PyLibs\32bit` 
        * Double-click on the `ArcGIS104_Py32_libs.bat` file
    * **ArcGIS 10.4.x (with 64-bit Background Geoprocessing)**:
        * Open the folder `PyLibs\64bit` 
        * Double-click on the `ArcGISx64104_Py64_libs.bat` file

## Install the R-ArcGIS tools 
---------------------

ArcGIS has developed a nice [Github webpage](https://github.com/R-ArcGIS/r-bridge-install) with lots of useful documentation on how to install a set of libraries to make sure R and ArcGIS can talk to each other.

Inside the .zip folder of the toolbox you will find another .zip folder called *r-bridge-install-master*. As the instructions in the webpage above point out, unzip the folder and open ArcMap. Go to the toolboxes menu, right-click and select to "add toolbox". Then, find the **R Integration.pyt** toolbox inside the unzipped folder and you should see a new toolbox appearing in the list of existing ones. At this point, follow the instructions from the github webpage above to make sure you have the correct R software version installed and install the appropriate libraries that ArcGIS and R need to talk to each other.

## Add the Telecoupling Toolbox to ArcGIS
---------------------

You are almost done! 

Inside the downloaded (unzipped) Telecoupling Toolbox folder, you will notice an ArcMap file (.mxd) called **TelecouplingApplication.mxd**. If you double-click on it, your ArcGIS will open and show a set of GIS layers used by the application as a basemap. Moreover, if you open the ArcToolbox tab, you should see the current version of the Telecoupling Toolbox already added to the list. Alternatively, you can open a brand new ArcMap document and follow the same procedure shown in the 'Install the R-ArcGIS tools' section to add the Telecoupling Toolbox. 

Inside the Telecoupling Toolbox you should see 5 toolsets (*__agents__*, *__causes__*, *__effects__*, *__flows__*, *__systems__*) and a number of python tool scripts inside each one of them. To learn more about what each tool script does and what parameters it takes, please refer to the help documentation that comes with it. To do so, you can either use ArcCatalog, clicking on the 'description' tab for a tool or, alternatively, click on the 'show help' button found at the bottom of each tool script after opening it (double-click on the tool script to open the user interface). 

## Test the tools using the sample data provided
---------------------

You can now start testing and using the toolbox using the set of sample data ('SampleData.zip') provided with this repository. After unzipping the sample data folder, you will see a mix of GIS (vector, raster) data and tables (.csv) needed as input parameters by the script tools. Follow the Telecoupling Toolbox User Guide found inside the Documentation folder and start testing the Telecoupling Toolbox!
