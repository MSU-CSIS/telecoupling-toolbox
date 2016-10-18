ECHO Adding 64-bit ArcGISx64 Python27 to system PATH...
SETX PATH "%PATH%;C:\Python27\ArcGISx6410.3;C:\Python27\ArcGISx6410.3\Scripts"
SET PATH=%PATH%C:\Python27\ArcGISx6410.3;C:\Python27\ArcGISx6410.3\Scripts
ECHO Installing Required Python Modules...
pip install GDAL-1.11.4-cp27-none-win_amd64.whl
pip install matplotlib-1.5.2-cp27-cp27m-win_amd64.whl
pip install numpy-1.11.1+mkl-cp27-cp27m-win_amd64.whl
pip install scipy-0.18.0rc2-cp27-cp27m-win_amd64.whl
pip install pyamg-2.3.2-cp27-none-win_amd64.whl
pip install Rtree-0.8.2-cp27-cp27m-win_amd64.whl
pip install Shapely-1.5.16-cp27-cp27m-win_amd64.whl
pip install natcap.versioner
pip install setuptools
pip install --upgrade --pre --no-deps pygeoprocessing
pip install natcap.invest
pip install bs4
pip install BeautifulSoup
PAUSE
