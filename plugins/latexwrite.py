import sys
from docutils import nodes
from sphinx.writers.latex import LaTeXTranslator
from wrapper import *
from sphinx import version_info as sphinx_version
#from sphinx.util import logging

#logger = logging.getLogger(__name__)


"""
This function overrides visit_literal_block() defined in
/usr/lib/pythonX/dist-packages/sphinx/writers/latex.py
It is called for every code-block:: encountered in the document tree
when writing output.tex
"""
def latex_visit_literal_block(self, node):
    code = node.astext()
    ellipsis = u'\u2026'	# UTF-8 ellipsis character '...'
    if sys.version_info >= (3, 5):
        utext = str(code)
    else:
        utext = unicode(code)
    if utext.find(ellipsis) > -1:
        utext = utext.replace(ellipsis, "...")
        #print('DEBUG:', utext)

    if sys.version_info >= (3, 5):
        code = utext
    else:
        try:
            code = utext.decode("ascii")
        except UnicodeError as err:
            #print('DEBUG: unknown unicode character', err.object[err.start:err.end])
            self.builder.warn("Unknown unicode character '%s' add ASCII conversion to 'plugins/codeblock.py'" % err.object[err.start:err.end], ('', node.line))
            raise nodes.SkipNode

    self.body.append('\\begin{lstlisting}\n' + code + '\n\\end{lstlisting}\n')
    raise nodes.SkipNode


def setup(app):
    add_node_wrapper(app, nodes.literal_block,
            latex=(latex_visit_literal_block, None))

