# -*- coding: utf8 -*-
"""

****************************
``helper/reserved_words.py``
****************************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``reserved_words.py`` is a helper module providing a list of reserved ``VHDL`` keywords, which should not be
used as identifiers in ``XML`` files used to generate the ``VHDL``.

"""
vhdl_reserved_words = ["abs", "access", "after", "alias", "all", "and", "architecture", "array", "assert", "attribute",
                       "begin", "block", "body", "buffer", "bus", "case", "component",
                       "configuration", "constant", "disconnect", "downto", "else", "elsif", "end", "entity", "exit",
                       "file", "for", "function", "generate", "generic", "group", "guarded",
                       "if", "impure", "in", "inertial", "inout", "is", "label", "library", "linkage", "literal",
                       "loop", "map", "mod", "nand", "new", "next", "nor", "not", "null", "of", "on", "open",
                       "or", "others", "out", "package", "port", "postponed", "procedure", "process", "pure", "range",
                       "record", "register", "reject", "return", "rol", "ror", "select", "severity",
                       "signal", "shared", "sla", "sli", "sra", "srl", "subtype", "then", "to", "transport", "type",
                       "unaffected", "units", "until", "use", "variable", "wait", "when", "while",
                       "with", "xnor", "xor"]