import uuid
import fieldlisttable
from docutils import nodes
from sphinx.roles import XRefRole
from backports import OrderedDict, OrderedSet
from sphinx.domains.std import StandardDomain
from sphinx import addnodes
from sphinx.writers.latex import LaTeXTranslator
from wrapper import *
from sphinx import version_info as sphinx_version
#import inspect

# Element classes

class page_ref(nodes.reference):
    pass

class num_ref(nodes.reference):
    pass


# Visit/depart functions

def skip_node(self, node):
    raise nodes.SkipNode


def latex_visit_page_ref(self, node):
    self.body.append("\\pageref{%s:%s}" % (node['refdoc'], node['reftarget']))
    raise nodes.SkipNode


"""
This function overrides visit_number_reference() (Sphinx >= v1.3.6) defined in
/usr/lib/pythonX/dist-packages/sphinx/writers/latex.py
Called for every :numref: encountered in the document tree when writing output.tex
Produces:
  numhyperref[xxx]{Table ref{xxx}}
instead of hyperref because ul{ref{xxx}} doesn't work
"""
def latex_visit_num_ref(self, node):
    """
    itemids = getattr(self.builder.env, 'itemids', {})

    fields = node['reftarget'].split('#')

    if len(fields) > 1:
        label, target = fields
    else:
        label = None
        target = fields[0]
        
    target = target.lower()

    if target not in self.builder.env.docnames_by_itemname:
        raise nodes.SkipNode
        
    targetdoc = self.builder.env.docnames_by_itemname[target]
    
    if label is None:
        if target in itemids:
            label = itemids[target]

    ref_link = '%s:%s' % (targetdoc, target)

    if label is None:
        latex = '\\ref{%s}' % ref_link
    else:
        # Use document reference commands for document section references
        if ref_link.find(":docref-") > -1:
            latex = "\\dochyperref[%s]{%s}" % (ref_link, label)
        else:
            latex = "\\hyperref[%s]{%s}" % (ref_link, label)

    """

    env = self.builder.env

    if node.get('refid'):
        tab_id = self.curfilestack[-1] + ':' + node['refid']
    else:
        if 'refuri' in node:
            tab_id = node.get('refuri', '')[1:].replace('#', ':')
        else:
            # This applies only if Sphinx <= v1.3.6 i.e. :numref: role doesn't exist and
            # references are created manually.
            tab_id = '#unknown#'
            env.warn('', ":numref:%s target is not known (missing 'refuri')" % node['reftarget'])
        #print('DEBUG:', tab_id)

    title = node.get('title', '%s')
    #title = text_type(title).translate(tex_escape_map).replace('\\%s', '%s')
    if '\\{name\\}' in title or '\\{number\\}' in title:
        # new style format (cf. "Fig.%{number}")
        title = title.replace('\\{name\\}', '{name}').replace('\\{number\\}', '{number}')
        #text = escape_abbr(title).format(name='\\nameref{%s}' % self.idescape(id),
        #                                     number='\\ref{%s}' % self.idescape(id))
        text = title.format(name='\\nameref{%s}' % tab_id,
                                             number='\\ref{%s}' % tab_id)
    else:
        # old style format (cf. "Fig.%s")
        #text = escape_abbr(title) % ('\\ref{%s}' % self.idescape(id))
        text = title % ('\\ref{%s}' % tab_id)

    hyperref = '{\\numhyperref[%s]{%s}}' % (tab_id, text)
    self.body.append(hyperref)
    raise nodes.SkipNode


"""
Sphinx <= v1.3.6
This function is called for every <table/> encountered in the document tree
when writing output.tex
We are adding table name to 'next_table_ids', it is used to produce
\label{xxx} by depart_table() function
Overrides StandardDomain.visit_table() defined in
/usr/lib/pythonX/dist-packages/sphinx/writers/latex.py
"""
def latex_visit_table(self, node):
    if hasattr(self, 'next_table_ids'):
        #print("DEBUG: LaTeXTranslator has 'next_table_ids' (Sphinx <= v1.3.6)")

        if not node['names'] == []:
            #print('DEBUG: visit_table:', node['names'])
            self.next_table_ids.update(node['names'])
        elif not node['ids'] == []:
            #print('DEBUG Sphinx v1.3.6 bug: table doesnt have [names], using [ids] instead ', node['ids'])
            self.next_table_ids.update(node['ids'])
        else:
            tabtitle = '???'
            #print('DEBUG: visit_table:', inspect.getmembers(node))

            if node.children[0] and isinstance(node.children[0], nodes.title):
                tabtitle = node.children[0].astext()
            self.builder.warn("Table '%s' doesn't have :name: and no [ids]" % tabtitle)

    self.original_visit_table(node)


"""
This function is called for every document read
"""
def doctree_read(app, doctree):
    env = app.builder.env

    if not app.builder.name in ('html', 'singlehtml', 'epub'):
        return;

    docname_items = getattr(env, 'docname_items', {})
    docnames_by_itemname = getattr(env, 'docnames_by_itemname', {})
    newId = 1

    for item_info in doctree.traverse(lambda n: isinstance(n, nodes.table)):
        
        if isinstance(item_info.parent, fieldlisttable.fieldlisttable):
            item_info['ids'] = item_info.parent['ids']
            item_info.parent['ids'] = []

        if item_info['ids'] == []:
            if not item_info['names'] == []:
                # Currently used '.. field-list-table::' has ':name:xxx' option
                item_info['ids'] = item_info['names']
                #print('DEBUG:', item_info['ids'])
            elif not item_info['dupnames'] == []:
                # Currently used '.. field-list-table::' has ':name:xxx' option
                # Sphinx v1.3.6 bug: uses 'dupnames' instead of 'names'
                item_info['ids'] = item_info['dupnames']
                #print('DEBUG:', item_info['ids'])
            else:
                # Legacy no target before '.. field-list-table::' and no ':name:xxx' option
                #print("table ==> ", item_info.traverse(nodes.title), " newId => ", env.docname + '-numref-' + str(newId))
                item_info['ids'].append(env.docname + '-numref-' + str(newId))
        else:
            # Legacy '.. _docref-UARTAttributes:' target before '.. field-list-table::'
            doctree.ids[item_info['ids'][0]] = item_info
            #print('DEBUG:', doctree.ids[item_info['ids'][0]])

        for id in item_info['ids']:
            docnames_by_itemname[id] = env.docname
            
            if env.docname not in docname_items:
                docname_items[env.docname] = OrderedDict()
            
            if id not in docname_items[env.docname]:
                docname_items[env.docname][id] = OrderedSet()
                
        newId += 1;
     
    env.docnames_by_itemname = docnames_by_itemname
    env.docname_items = docname_items


"""
This function is called once after all doctrees have been resolved
doctree argument is the resulting tree, it is not the same as argument of doctree_read()
"""
def doctree_resolved(app, doctree, docname):
    env = app.builder.env
    domain = env.domains['std']

    if app.builder.name in ('html', 'singlehtml', 'epub') and not hasattr(env, 'toc_fignumbers'):
        #print('DEBUG: toc_fignumbers doesnt exist (Sphinx <= v1.2.2)')
        itemids = getattr(env, 'itemids', {})

        secnums = []
        itemnames_by_secnum = {}

# get section numbers
        for figdocname, figurelist in env.docname_items.iteritems():
            if figdocname not in env.toc_secnumbers:
                #print('DEBUG: not in sectnumbers:', figdocname, env.toc_secnumbers)
                continue

            secnum = env.toc_secnumbers[figdocname]['']
            secnums.append(secnum)
            itemnames_by_secnum[secnum] = figurelist

# add section numbers to table numbers        
        last_secnum = 0
        secnums = sorted(secnums)
        tableIndex = 1
        for secnum in secnums:
            if secnum[0] != last_secnum:
                tableIndex = 1

            for itemname, subitems in itemnames_by_secnum[secnum].iteritems():
                itemids[itemname] = str(secnum[0]) + '.' + str(tableIndex)
                #print('DEBUG: itemname ==> ', itemname , ' ==> ', itemids[itemname])
                tableIndex += 1
            last_secnum = secnum[0]

        env.itemids = itemids

# resolve table number from 'toc_fignumbers' or 'itemids' and add to table titles
    if app.builder.name in ('html', 'singlehtml', 'epub'):
        #print('DEBUG: Add "Table x.x" before table title')
        for item_info in doctree.traverse(lambda n: isinstance(n, nodes.table)):
            for tab_id in item_info['ids']:
                if hasattr(env, 'toc_fignumbers'):
                    #print('DEBUG: toc_fignumbers exists (Sphinx >= v1.3.6)')
                    if tab_id not in env.docnames_by_itemname:
                        env.warn('', "table ID '%s' is not found in env.docnames_by_itemname" % tab_id)
                        continue

                    dname = env.docnames_by_itemname[tab_id]
                    try:
                        tabnum = env.toc_fignumbers[dname]['table'][tab_id]
                    except (KeyError, IndexError):
                         env.warn('', 'no number is assigned for %s: %s' % (dname, tab_id))
                         continue

                    tabnumber = '%s' % '.'.join(map(str, tabnum))
                    #print('DEBUG:', tab_id, tabnumber)
                else:
                    #print('DEBUG: toc_fignumbers doesnt exist (Sphinx <= v1.2.2)')
                    if tab_id not in itemids:
                        env.warn('', "table ID '%s' is not found in itemids" % tab_id)
                        continue

                    tabnumber = itemids[tab_id]

                for title in item_info.traverse(nodes.title):
                    title_content = nodes.Text('%s %s %s' % (app.config.table_title_prefix, tabnumber, title[0]))
                    title[0] = nodes.strong('', title_content)

# add numbers to references
    for refnode in doctree.traverse(num_ref):
        #print('DEBUG: 'numref' role is not defined (Sphinx <= v1.2.2)')
        refTarget = refnode['reftarget'].lower()

        if app.builder.name in ('html', 'singlehtml', 'epub'):
            if '#' in refTarget:
                label, target = refTarget.split('#')
                labelfmt = label + " %s"
            else:
                labelfmt = 'Table %s'
                target = refTarget

            if target not in env.docnames_by_itemname or target not in itemids:
                app.warn('Target not found: %s in file %s' % (target, refnode['refdoc']))
                link = "#%s" % target
                linktext = target
            else:
                target_doc = env.docnames_by_itemname[target]

                if app.builder.name == 'singlehtml':
                    link = "#%s" % target
                else:
                    link = "%s#%s" % (app.builder.get_relative_uri(docname, target_doc),
                                      target)

                linktext = labelfmt % itemids[target]

            html = '<a class="reference" href="%s"><span class="std-numref">%s</span></a>' % (link, linktext)
            refnode.replace_self(nodes.raw(html, html, format='html'))

        elif app.builder.name in ('latex'):
            # Adapted from resolve_xref()
            if refTarget in domain.data['labels']:
                docname, labelid, figname = domain.data['labels'].get(refTarget, ('', '', ''))
            else:
                docname, labelid = domain.data['anonlabels'].get(refTarget, ('', ''))

            if not docname:
                app.warn('Target not found: %s' % (refTarget))
                continue

            target_node = env.get_doctree(docname).ids.get(labelid)
            if isinstance(target_node, nodes.table):
                refnode['title'] = app.config.table_title_prefix + ' %s'

            refnode['refuri'] = '%' + docname
            if labelid:
                refnode['refuri'] += '#' + labelid



def setup(app):
    app.add_config_value('table_title_prefix', 'Table', True)

    app.add_node(page_ref,
                 text=(skip_node, None),
                 html=(skip_node, None),
                 singlehtml=(skip_node, None),
                 latex=(latex_visit_page_ref, None))

    app.add_role('pageref', XRefRole(nodeclass=page_ref))

    if 'numref' in StandardDomain.roles:
        #print("DEBUG: 'numref' role is defined in /usr/lib/pythonX/dist-packages/sphinx/domains/std.py (Sphinx >= v1.3.6)")
        setattr(LaTeXTranslator, 'original_visit_number_reference', LaTeXTranslator.visit_number_reference)
        setattr(LaTeXTranslator, 'visit_number_reference', latex_visit_num_ref)
    else:
        #print("DEBUG: 'numref' role is not defined in /usr/lib/pythonX/dist-packages/sphinx/domains/std.py (Sphinx <= v1.2.2)")
        app.add_node(num_ref,
                 latex=(latex_visit_num_ref, None),
                 text=(skip_node, None))

        app.add_role('numref', XRefRole(lowercase=True, nodeclass=num_ref))

    if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] < 8)):
        app.connect('doctree-read', doctree_read)
        app.connect('doctree-resolved', doctree_resolved)

    setattr(LaTeXTranslator, 'original_visit_table', LaTeXTranslator.visit_table)
    setattr(LaTeXTranslator, 'visit_table', latex_visit_table)

