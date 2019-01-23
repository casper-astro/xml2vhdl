# -*- coding: utf-8 -*-
################################################################################
# Automatically Generated Settings (DO NOT MODIFY)
################################################################################
import os
import sys

sys.path.append(os.path.abspath('../../../scripts/python/xml2vhdl'))
sys.path.append(os.path.abspath('../../../scripts/python/xml2vhdl/example_slave'))
sys.path.append(os.path.abspath('../../../scripts/python/xml2vhdl/helper'))

project = u'XML2VHDL'
copyright = u'2019, University of Oxford'
author = u'Department of Physics'
version = u'2019.1'
release = u''
master_doc = 'index'
htmlhelp_basename = 'XML2VHDLdoc'
latex_documents = [
    (master_doc, 'XML2VHDL.tex', u'XML2VHDL Documentation',
     u'Department of Physics', 'manual'),
]
man_pages = [
    (master_doc, 'xml2vhdl', u'XML2VHDL Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'XML2VHDL', u'XML2VHDL Documentation',
     author, 'XML2VHDL', '',
     'Miscellaneous'),
]
html_theme_options = {
    'logo_only': False,
    'navigation_depth': 4,
    'collapse_navigation': False,
}
html_logo = '_static/logo.png'
html_static_path = ['_static']
html_context = {
    'css_files': ['_static/css/regtables.css'],
}

releases_unstable_prehistory = True
releases_release_uri = 'https://bitbucket.org/ricch/xml2vhdl/src/%s'

################################################################################
# The following Settings are Copied from Template File:
# /data2/users/mjr59/local_svn_working_copy/tools/fpgaflow/scripts/python/fpgaflow/templates/sphinx/1.8.2/templates/conf.py
################################################################################
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'releases',
    'breathe',
]

templates_path = ['_templates']
source_suffix = ['.rst', '.md']
language = None
exclude_patterns = []
pygments_style = 'rainbow_dash'
html_theme = 'sphinx_rtd_theme'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

epub_title = project
epub_exclude_files = ['search.html']
todo_include_todos = True
