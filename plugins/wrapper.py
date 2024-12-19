
from sphinx import version_info as sphinx_version

# logging module exists in Sphinx >= v1.8.5
if (sphinx_version[0] > 1 or (sphinx_version[0] == 1 and sphinx_version[1] >= 8)):
    from sphinx.util import logging
    logger = logging.getLogger(__name__)


"""
This is wrapper for add_node() function defined in
/usr/lib/pythonX/dist-packages/sphinx/application.py
Sphinx < v1.8.5	def add_node(self, node, **kwds):
Sphinx >= v1.8.5	def add_node(self, node, override=False, **kwds):
"""
def add_node_wrapper(app, node, **kwds):
    if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] < 8)):
        app.add_node(node, **kwds)
    else:
        app.add_node(node, True, **kwds)


"""
This is used to print a warning message
Sphinx < v1.8.5	def warn_node(self, msg, node):  /usr/lib/pythonX/dist-packages/sphinx/environment.py
Sphinx >= v1.8.5	def warning(self, msg, *args, **kwargs): /usr/lib/pythonX/logging/__init__.py
"""
def sphinx_warning(env, msg, node):
    if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] < 8)):
        env.warn_node(msg, node)
    else:
        logger.warning(msg + '%s', '', location=node)
