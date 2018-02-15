# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join('..', 'sphinx-template'))
from utils import get_month_year, get_year

# -- General configuration ------------------------------------------------

# General information about the project.
project = u'GISMentors: GRASS GIS Workshop in Jena'
copyright = u'%d GISMentors.eu' % get_year()

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0'
# The full version, including alpha/beta/rc tags.
release = '%s' % version

# -- Options for HTML output ----------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'grass-gis-workshop-jena-2018-gismentors'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# Additional stuff for the LaTeX preamble.
    'preamble': "".join([]),
    'releasename': u'version',
    'date': '%s %s' % get_month_year(),
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', '%s-%s.tex' % (htmlhelp_basename, version), project,
     u'GISMentors', u'manual'),
    ]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', htmlhelp_basename, project,
     [copyright], 1)
    ]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', htmlhelp_basename, project,
     copyright, htmlhelp_basename, project,
     'Miscellaneous'),
    ]

html_favicon = "images/favicon.ico"

from conf_base import *

todo_include_todos = True
html_use_index = False
language = 'en'
