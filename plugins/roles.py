# -*- coding: utf-8 -*-

from six import iteritems
from docutils import nodes
from docutils.parsers.rst import roles, states
from docutils.parsers.rst.states import Body
from sphinx.domains.std import StandardDomain
from wrapper import *
#import inspect


autoTargRoles = ['xmlattr']
refStyles = ['xmlattr', 'xmlelem', 'xmlgroup', 'docref', 'bitref']
ourLabel = 'lelabel'
bitdefRole = 'bitdef'


# Get file name from path
def name_from_path(self, filepath):
    filename = filepath

    delim = filepath.rfind('/')
    if delim > -1:
        filename = filepath[delim+1:]

    delim = filename.rfind('.')
    if delim > -1:
        filename = filename[:delim]
    return nodes.make_id(filename)


# Traverse up parent nodes and look for a source attribute which contains path of the source file
def find_source(self, node):
    if not node.source == None:
        return node.source
    if not node.parent == None:
        return self.find_source(node.parent)
    return None


# Get 'sectprefix' from options
def get_prefix(role, rawtext, text, lineno, inliner, userpref, options):
    # Substitute 'class' with 'classes'
    roles.set_classes(options)

    if not userpref in options:
        inliner.reporter.warning('"%s" option is not defined for autotarget role :%s:%s' %
              (userpref, role, text))
        return None

    prefix = options[userpref]
    del options[userpref]
    return prefix


"""
This is a custom role (:xmlattr:) that creates a link target (text).
Class of the link target is set as the name of this role e.g. 'xmlattr'
    html -> <inline class="xmlattr">ASDUAddr</inline>
    pdf -> \DUrole{xmlattr}{ASDUAddr}
Reference target is created for each instance as follows:
    'xmlattr-' + last section target 'xmlelem-' + label e.g. 'xmlattr-gp101maasduaddr'
Called for every :xmlattr: encountered in source files by Inliner.interpreted() defined in
/usr/lib/pythonX/dist-packages/docutils/parsers/rst/states.py
"""
def autotarget_role(role, rawtext, text, lineno, inliner,
                        options={}, content=[]):
    secTarg = None
    sectprefix = get_prefix(role, rawtext, text, lineno, inliner, 'sectprefix', options)

    # This calls TextElement.__init__() in /usr/lib/pythonX/dist-packages/docutils/nodes.py
    inode = nodes.inline(rawtext, text, **options)

    if sectprefix == None:
        return [inode], []

    #source = find_source(inliner.parent)
    #if source == None:
    #    inliner.reporter.warning('Cant get the name of the source file where :%s:%s at line %s is defined' %
    #        (role, text, lineno))
    #else:
    #    filename = name_from_path(source)

    # Traverse all existing <target> nodes and use the last one that conains 'xmlelem-' as sectionname for our xmlattr
    for snode in inliner.document.traverse(nodes.target, False, True, False, False):
        for sectid in snode['ids']:
            if sectprefix in sectid:
                secTarg = sectid[len(sectprefix):]
                #print('DEBUG: Section ID:', sectid)

    # This is an alternative to use a source file name in case 'xmlelem-' is not found
    # if secTarg == None:
    #     secTarg = filename

    if secTarg == None:
        inliner.reporter.warning('There is no "%s" defined before ":%s:%s" at line %s' %
            (sectprefix, role, text, lineno))
        return [inode], []

    ourid = role + '-' + secTarg + nodes.make_id(text)
    if ourid in inliner.document.ids:
        inliner.reporter.warning('Target "%s" already defined, make sure there is "%s" before :%s:%s at line %s' %
                (ourid, sectprefix, role, text, lineno))
        return [inode], []

    tnode = nodes.target('', '', **options)
    tnode.append(inode)
    tnode['names'] = [ourid]
    tnode['ids'] = [ourid]
    #print('DEBUG: autoref:', ourid)
    inliner.document.note_explicit_target(tnode)
    return [tnode], []


"""
This is a custom role (:bitdef:) that creates a link target (text).
Class of the link target is set as the name of this role 'bitdef'
    html -> <inline class="bitdef">Bit 0</inline>
    pdf -> \DUrole{bitdef}{Bit 0}
Reference target is created in build_bitrefs() function.
Called for every :bitdef: encountered in source files by Inliner.interpreted() defined in
/usr/lib/pythonX/dist-packages/docutils/parsers/rst/states.py
"""
def bitdef_role(role, rawtext, text, lineno, inliner,
                        options={}, content=[]):
    origopts = options.copy()
    tabprefix = get_prefix(role, rawtext, text, lineno, inliner, 'tabprefix', options)

    # This calls TextElement.__init__() in /usr/lib/pythonX/dist-packages/docutils/nodes.py
    inode = nodes.inline(rawtext, 'Bit ' + text, **options)

    if tabprefix == None:
        return [inode], []

    tnode = nodes.target('', '', **origopts)
    tnode.append(inode)
    tnode['bitnum'] = text
    #print('DEBUG: bitdef_role: %s' % (rawtext))
    #print('DEBUG: bitdef_role:', inspect.getmembers(inliner.parent.parent))
    return [tnode], []


"""
Build a reference target for :bitdef:.
Reference target is created for each instance as follows:
    'bitref-' + table name 'tabid-' + bit number e.g. 'bitref-spabusmaappflagsbit0'
Called from fieldlisttable.py after table has been built.
'bitref-' is deliberately different from role name :bitdef: because we need different
classes for styling link targets (Bit 0) and references (<a><span class="bitref">Bit[0]</span></a>)
"""
def build_bitrefs(self, tableNode):
    for target in tableNode.traverse(nodes.target, False, True, False, False):
        if bitdefRole in target['classes']:
            tabTitle = '???'
            target['ids'] = []

            for title in tableNode.traverse(nodes.title):
                tabTitle = title.astext()

            if tableNode['ids'] == []:
                self.state_machine.reporter.warning('Table "%s" doesnt have [ids]' % (tabTitle))
            elif not target.hasattr('tabprefix'):
                self.state_machine.reporter.warning(':%s: role doesnt have [tabprefix]' % (bitdefRole))
            else:
                # Use full table id in case table name doesn't contain 'tabid-'
                tabTarg = tableNode['ids'][0]
                for tid in tableNode['ids']:
                    if target['tabprefix'] in tid:
                        tabTarg = tid[len(target['tabprefix']):]
                        break

                ourid = 'bitref-' + tabTarg + 'bit' + target['bitnum']

                if ourid in self.state_machine.document.ids:
                    self.state_machine.reporter.warning('Target "%s" already defined, make sure tables have unique names' % (ourid))
                else:
                    target['ids'] = [ourid]
                    target['names'] = [ourid]
                target.delattr('tabprefix')

            self.state_machine.document.note_explicit_target(target)
            #print('DEBUG: build_bitrefs:', target)


"""
Overrides Body.add_target() defined in
/usr/lib/pythonX/dist-packages/docutils/parsers/rst/states.py
! This is not API !
If target (refuri) contains 'lelabel=' keyword, remove it and
create attribute in the target node e.g. <target lelabel="xxx"/>
"""
def our_add_target(self, targetname, refuri, target, lineno):
     if not refuri == '' and ourLabel + '=' in refuri:
         target[ourLabel] = refuri[len(ourLabel)+1:]
         refuri = None
         #print('DEBUG: add_target: %s %s' % (targetname, target))
     self.original_add_target(targetname, refuri, target, lineno)


"""
Overrides StandardDomain.process_doc() API (check StandardDomain.note_labels() in Sphinx >= 1.8.5) defined in
/usr/lib/pythonX/dist-packages/sphinx/domains/std.py
Called for every document source file by SphinxDomains.apply() defined in
/usr/lib/pythonX/dist-packages/sphinx/transforms/references.py
1/ Add XML attribute names defined by :xmlattr:'xxx' to document.data['labels'] array.
2/ Add Bit numbers defined by :bitdef:'xxx' to document.data['labels'] array.
3/ Ammend document.data['labels'] entries
   Replace section names automatically created by PropagateTargets.apply() from '.. _xmlelem-xxx' with custom 'lelabel'.
   /usr/lib/pythonX/dist-packages/docutils/transforms/references.py
document.data['labels'] array is used to automatically create labels for references i.e. :ref:'link_to_something' becomes 'something'
"""
def our_process_doc(self, env, docname, document):
    self.original_process_doc(env, docname, document)
    labels = self.data['labels']
    # Add :xmlattr:'xxx' labels to document.data['labels'] array
    # Add :bitdef:'xxx' labels to document.data['labels'] array
    for name, explicit in iteritems(document.nametypes):
        if not explicit:
            continue
        labelid = document.nameids[name]
        if labelid is None:
            continue
        node = document.ids[labelid]
        classes = node['classes']
        if classes == []:
            continue

        for cls in classes:
            if cls in autoTargRoles:
                #sphinx_warning(env, 'DEBUG: process_doc: %s' % node, node)
                #print('DEBUG: process_doc: %s' % (node))
                if name in labels:
                    sphinx_warning(env, 'duplicate label %s, other instance in %s' %
                                   (name, env.doc2path(labels[name][0])), node)
                labels[name] = docname, labelid, node.astext()
                break

            elif cls == bitdefRole:
                #print('DEBUG: process_doc: %s' % (node))
                if name in labels:
                    sphinx_warning(env, 'duplicate label %s, other instance in %s' %
                                   (name, env.doc2path(labels[name][0])), node)
                labels[name] = docname, labelid, 'Bit[' + node['bitnum'] + ']'
                break

    # Substitute section name in document.data['labels'] array with
    # Label defined as part of .. _xmlelem-linkname lelabel=xxx
    for target in document.traverse(nodes.target, False, True, False, False):
        if ourLabel in target:
            tid = target['refid']
            if tid in labels:
                odocname, labelid, sectname = labels[tid]
                labels[tid] = odocname, labelid, target[ourLabel]
                #print('DEBUG: process_doc: %s %s %s' % (labels[tid]))


"""
Overrides StandardDomain.resolve_xref() API (check StandardDomain.build_reference_node() in Sphinx >= 1.8.5) defined in
/usr/lib/pythonX/dist-packages/sphinx/domains/std.py
If reference contains 'xmlattr' e.g. :ref:'xmlattr-gp101maasduaddr',
update class of the inline node i.e. <inline classes="xmlattr"/>
This will result in links that are easy to style:
    html -> <a class="reference internal" href="#xmlattr-gp101maasduaddr"><span class="xmlattr">ASDUAddr</span></a>
    pdf -> \hyperref[xxx]{\sphinxcrossref{\DUrole{xmlattr}{ASDUAddr}}
We can create custom classes for styling references e.g. 'refxmlattr' if becomes necessary in the future.
"""
def our_resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
    refnode = self.original_resolve_xref(env, fromdocname, builder, typ, target, node, contnode)
    if not typ == 'ref' or refnode == None:
        return refnode

    for key in refStyles:
        if key + '-' in target:
            for child in refnode.children:
                # Sphinx >= 1.8.5
                if isinstance(child, nodes.inline):
                    child['classes'] = [key]
                    #print('DEBUG resolve_xref:', child)
                # Sphinx < 1.8.5
                # Replace <emphasis> with <inline>
                elif isinstance(child, nodes.emphasis):
                    content = child.astext()
                    refnode.remove(child)
                    child = nodes.inline(content, content)
                    child['classes'] = [key]
                    refnode.append(child)
                    #print('DEBUG resolve_xref:', child)
            break
    return refnode


"""
class CustomRole defined in
/usr/lib/pythonX/dist-packages/docutils/parsers/rst/roles.py
"""
def register_role(name):
    base_role = roles.generic_custom_role
    role = roles.CustomRole(name, base_role, {'class': [name]}, [])
    roles.register_local_role(name, role)


def register_roles(app):
    for name in app.builder.config.roles:
        register_role(name)
    for name in autoTargRoles:
        role = roles.CustomRole(name, autotarget_role, {'classes': [name], 'sectprefix' : 'xmlelem-'}, [])
        roles.register_local_role(name, role)
    role = roles.CustomRole(name, bitdef_role, {'classes': [bitdefRole], 'tabprefix' : 'tabid-'}, [])
    roles.register_local_role(bitdefRole, role)


def setup(app):
    app.add_config_value('roles', [], True)
    app.connect("builder-inited", register_roles)

    setattr(Body, 'original_add_target', Body.add_target)
    setattr(Body, 'add_target', our_add_target)
    # In theory new subdomain can be created from StandardDomain where these methods can be overwritten
    setattr(StandardDomain, 'original_process_doc', StandardDomain.process_doc)
    setattr(StandardDomain, 'process_doc', our_process_doc)
    setattr(StandardDomain, 'original_resolve_xref', StandardDomain.resolve_xref)
    setattr(StandardDomain, 'resolve_xref', our_resolve_xref)

