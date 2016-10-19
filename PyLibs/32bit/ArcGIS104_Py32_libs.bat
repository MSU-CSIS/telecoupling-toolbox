@echo off
SET PATH=%PATH%C:\Python27\ArcGIS10.4;C:\Python27\ArcGIS10.4\Scripts
pip install GDAL-1.11.3-cp27-none-win32.whl
pip install matplotlib-1.5.3-cp27-cp27m-win32.whl
pip install numpy-1.11.2+mkl-cp27-cp27m-win32.whl
pip install scipy-0.18.1-cp27-cp27m-win32.whl
pip install pyamg-2.3.2-cp27-none-win32.whl
pip install Rtree-0.8.2-cp27-cp27m-win32.whl
pip install Shapely-1.5.17-cp27-cp27m-win32.whl
pip install natcap.versioner
pip install setuptools
pip install pygeoprocessing==0.3.0a22
pip install natcap.invest==3.3.1
pip install bs4
pip install BeautifulSoup
PAUSE
