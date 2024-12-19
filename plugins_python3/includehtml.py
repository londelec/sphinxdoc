import os.path
import re
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives
from sphinx.directives.other import Include as BaseInclude


class inchtml(nodes.raw):
    pass


class HtmlInclude(BaseInclude):

    option_spec = {'encoding': directives.encoding,
                   'tab-width': int,
                   'start-after': directives.unchanged_required,
                   'end-before': directives.unchanged_required,
                   'latex-tip': directives.unchanged,
                   'caption': directives.unchanged,
                   'name': directives.unchanged}


    def run(self):
        """
        Copied from /usr/lib/pythonX/dist-packages/sphinx/directives/other.py
        class Include(BaseInclude):
        """
        env = self.state.document.settings.env
        rel_filename, filename = env.relfn2path(self.arguments[0])
        #self.arguments[0] = filename
        path = directives.path(filename)

        """
        Copied from /usr/lib/pythonX/dist-packages/docutils/parsers/rst/directives/misc.py
        class Include(Directive):
        """
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        #path = directives.path(self.arguments[0])
        #if path.startswith('<') and path.endswith('>'):
        #    path = os.path.join(self.standard_include_path, path[1:-1])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        path = nodes.reprunicode(path)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)
        e_handler=self.state.document.settings.input_encoding_error_handler
        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        try:
            self.state.document.settings.record_dependencies.add(path)
            include_file = io.FileInput(source_path=path,
                                        encoding=encoding,
                                        error_handler=e_handler)
        except UnicodeEncodeError as error:
            raise self.severe(u'Problems with "%s" directive path:\n'
                              'Cannot encode input file path "%s" '
                              '(wrong locale?).' %
                              (self.name, SafeString(path)))
        except IOError as error:
            raise self.severe(u'Problems with "%s" directive path:\n%s.' %
                      (self.name, ErrorString(error)))
        #startline = self.options.get('start-line', None)
        #endline = self.options.get('end-line', None)
        try:
            #if startline or (endline is not None):
            #    lines = include_file.readlines()
            #    rawtext = ''.join(lines[startline:endline])
            #else:
                rawtext = include_file.read()
        except UnicodeError as error:
            raise self.severe(u'Problem with "%s" directive:\n%s' %
                              (self.name, ErrorString(error)))
        # start-after/end-before: no restrictions on newlines in match-text,
        # and no restrictions on matching inside lines vs. line boundaries
        after_text = self.options.get('start-after', None)
        if after_text:
            # skip content in rawtext before *and incl.* a matching text
            after_index = rawtext.find(after_text)
            if after_index < 0:
                raise self.severe('Problem with "start-after" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[after_index + len(after_text):]
        before_text = self.options.get('end-before', None)
        if before_text:
            # skip content in rawtext after *and incl.* a matching text
            before_index = rawtext.find(before_text)
            if before_index < 0:
                raise self.severe('Problem with "end-before" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[:before_index]

        #print('DEBUG:', self.options.get('name', None))
        if env.app.builder.name in ('html', 'singlehtml', 'epub'):
            #print('DEBUG: HTML detected', env.app.builder.name)
            # Remove tabs and whitespaces from the beging of lines
            htmltext = ''
            for sline in rawtext.splitlines():
                whitespace = re.compile('^[\t ]*')
                sline = whitespace.sub('', sline)
                if sline == '':
                    continue;
                #print('DEBUG: empty sline', sline)
                htmltext += sline + '\n'

            """
            Copied from /usr/lib/pythonX/dist-packages/docutils/parsers/rst/directives/misc.py
            class Raw(Directive):
            """
            attributes = {'format': 'html'}
            attributes['source'] = path
            raw_node = inchtml(htmltext, '', **attributes)
            #raw_node = nodes.raw('', htmltext, **attributes)
            (raw_node.source,
            raw_node.line) = self.state_machine.get_source_and_line(self.lineno)

            caption_text = self.options.get('caption', None)
            if caption_text:
                caption_node = nodes.caption('', caption_text, **attributes)
                raw_node += caption_node
                (caption_node.source,
                caption_node.line) = self.state_machine.get_source_and_line(self.lineno)
            return [raw_node]
        else:
            latex_tip = self.options.get('latex-tip', None)
            if latex_tip:
                #print('DEBUG: latex_tip', latex_tip)
                tip_node = nodes.tip(latex_tip, source=path,
                                     classes=self.options.get('class', []))
                self.add_name(tip_node)
                tip_node += nodes.Text(latex_tip, latex_tip)
                return [tip_node]
        return []


def html_visit_inchtml(self, node):
    if 'html' in node.get('format', '').split():
        self.body.append(self.starttag(node, 'div', '', CLASS='inchtml'))
        #self.body.append(node.astext())
        self.body.append(node.rawsource)


def html_depart_inchtml(self, node):
    self.body.append('</div>')


def setup(app):
    app.add_directive('include-html', HtmlInclude)

    app.add_node(inchtml,
                 html=(html_visit_inchtml, html_depart_inchtml),
                 singlehtml=(html_visit_inchtml, html_depart_inchtml))

