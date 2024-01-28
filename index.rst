************
Introduction
************

Free and Open Source Software (FOSS)
====================================

.. figure:: ./images/foss.png
   :class: small
        
   FOSS software overview (`source
   <https://www.linkedin.com/pulse/open-source-software-development-neha-sharma>`__).

Free and open-source software (FOSS) is a computer software that can be
classified as both **free software** and **open-source
software**. That is, anyone is freely licensed to

* use,
* copy,
* study, and
* change

the software in any way. The source code is openly shared so that
people are encouraged to voluntarily improve the design of the
software. This is in contrast to **proprietary software**, where the
software is under restrictive copyright and the source code is usually
hidden from the users. See :wikipedia:`Free and open-source
software` article on Wikipedia for more information.

FOSS for Geospatial
-------------------

In 2006 was founded `OSGeo Foundation <http://www.osgeo.org>`__ to
support the collaborative development of open source geospatial
software, and promote its widespread use.

.. figure:: ./images/osgeo-logo.png
   :class: small
   
   OSGeo logo (`source <https://www.osgeo.org/about/branding-material/>`__)

The foundation has adopted principles to ensure that projects under
OSGeo umbrella will satisfy basic quality requirements, namely:

* Projects should manage themselves, striving for consensus and
  encouraging participation from all contributors - from beginning
  users to advanced developers.
* Contributors are the scarce resource and successful projects court
  and encourage them.
* Projects are encouraged to adopt open standards and collaborate with
  other OSGeo projects.
* Projects are responsible for reviewing and controlling their code
  bases to insure the integrity of the open source baselines.

This principles ensure that `OSGeo projects
<https://www.osgeo.org/projects/>`__ are well established, stable,
mature and sustainable.

Software used in this training materials
========================================

.. figure:: ./images/grass-gis-logo.png
   :class: small
          
* `GRASS GIS <http://grass.osgeo.org>`__ (recommended version 8.3) for
  geospatial raster, imagery, and vector data processing and providing
  spatial analysis.
* `QGIS desktop <http://qgis.org>`__ (recommended version 3.28) for
  geospatial visualization, creating hardcopy outputs, and data
  publishing.
* `GDAL library <http://gdal.org>`__ for reading and writing various
  geospatial data.
* `sentinelsat library <https://pypi.python.org/pypi/sentinelsat>`__
  utility to search and download Copernicus Sentinel satellite images.
* `pyModis <http://www.pymodis.org/>`__ Python based library to work
  with MODIS data.
* `pyWPS <http://pywps.org/>`__ implementation of the Web Processing
  Service standard from the Open Geospatial Consortium written in
  Python.

Installation notes
------------------

Debian/Ubuntu Linux
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash
           
   sudo apt install grass

MS Windows
^^^^^^^^^^

* Install GRASS GIS 8 using `standalone installer
  <https://grass.osgeo.org/download/windows/#standalone-installers>`__

Sample dataset
==============

For purpose of this training materials a sample dataset has been
created based on Open Data covering Germany and Jena region
specifically. Sample dataset is split into four parts:

* `jena-sample-data-base.7z <https://geo.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2022/jena-sample-data-base.7z>`__ (294MB) [Units 1-17]
* `jena-sample-data-lidar.7z <https://geo.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2022/jena-sample-data-lidar.7z>`__ (541MB) [Units 18-19]
* `jena-sample-data-sentinel.7z <https://geo.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2022/jena-sample-data-sentinel.7z>`__ (1.7GB)
* `jena-sample-data-modis.7z <https://geo.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2022/jena-sample-data-modis.7z>`__ (1.0GB)
  
It is recommended to have at least 10GB free space (GRASS GIS
installation + sample data + computation results).

List of data sources used for sample dataset:

* EU-DEM (directory: :file:`eu-dem`, source: `Copernicus Land Monitoring
  Service - EU-DEM
  <https://www.eea.europa.eu/data-and-maps/data/copernicus-land-monitoring-service-eu-dem>`__)
* Sample GRASS locations/mapsets (directory: :file:`grassdata`)
* Lidar LAZ data (directory: :file:`lidar`, source: `GeoPortal Th
  <https://www.geoportal-th.de>`__)
* MODIS Land Surface Temperature eight day 1 Km (directory:
  :file:`modis`, source: `LP DAAC
  <https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table>`__)
* Administrative regions (directory: :file:`osm`, source:
  OpenStreetMap)
* Sentinel-2 data (directory: :file:`sentinel`, source: `Copernicus
  Open Access Hub <https://scihub.copernicus.eu/>`__)

Units
=====

`Time Schedule
<https://docs.google.com/spreadsheets/d/1usoz9TaWb2mlWtq5EgaHA6f3dB_oeBYMC_ovwPSB_Ns/edit?usp=sharing>`__

.. toctree::
   :maxdepth: 2

   units/01
   units/02
   units/03
   units/04
   units/05
   units/06
   units/07
   units/08
   units/09
   units/10
   units/11
   units/12
   units/13
   units/14
   units/15
   units/16
   units/17
   units/18
   units/19
   units/20
   units/21
   units/22
   units/23
   units/24
   units/25
   units/26
   units/27
   units/28
   units/29
   units/30

Lecturer
========

* `Martin Landa <http://geo.fsv.cvut.cz/gwiki/Landa>`__, GeoForAll
  Lab, Czech Technical University in Prague, Czech Republic

Materials proudly provided by `GISMentors
<http://www.gismentors.eu>`__ training and mentoring group.

License
=======

`Creative Commons Attribution-ShareAlike 4.0 International License
<http://creativecommons.org/licenses/by-sa/4.0/>`_.

.. figure:: ./images/cc-by-sa.png 
   :width: 130px
   :scale-latex: 120

Source code available on `GitHub
<https://github.com/GISMentors/grass-gis-workshop-jena>`__. Feel
free to open issues or pull requests to improve the materials :-)

*Document version:* |release| (built |today|)
