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
          
* `GRASS GIS <http://grass.osgeo.org>`__ (recommended version 7.8) for
  geospatial raster, imagery, and vector data processing and providing
  spatial analysis.
* `QGIS desktop <http://qgis.org>`__ (recommended version 3.4) for
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

Dataset
=======

For purpose of this training materials a sample dataset has been
created based on Open Data covering Germany and Jena region. See
detailed description below.

* administrative borders (directory: :file:`osm`, source:
  OpenStreetMap)

.. todo:: add list of layers, update links

Download sample dataset as `7z archive
<http://geo102.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2020/jena-data.7z>`__
(xxGB, xxGB uncompressed).

Virtual machine
===============

The simplest way how to follow this training. `VirtualBox
<http://virtualbox.org>`__ must be installed on your PC, enable also
*virtualization support* in BIOS. See `Virtualization Quickstart
<https://live.osgeo.org/en/quickstart/virtualization_quickstart.html>`__
for details.

A customized virtual machine (VM) below is based on `OSGeoLive
<http://live.osgeo.org>`__ version 13. This VM contains all software
dependecies including sample dataset in :file:`geodata` directory.

Download tailored virtual machine **including sample dataset** as `7z
archive
<http://geo102.fsv.cvut.cz/geoforall/grass-gis-workshop-jena-2018/osgeo-live-11.0-vm.7z>`__
(xxGB, xxGB uncompressed).

.. todo:: update links

Units
=====

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

..
   Timetable
   `[here] <https://docs.google.com/spreadsheets/d/1im4Yx_us0m1KfKxruJ2Un7chAlh6fxudlrxjVVK9UaE/edit?usp=sharing>`__

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
