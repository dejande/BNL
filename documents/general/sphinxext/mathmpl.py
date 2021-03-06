import os
import sys
from subprocess import call 
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from docutils import nodes
from docutils.parsers.rst import directives
import warnings

from matplotlib import rcParams
from matplotlib.mathtext import MathTextParser
rcParams['mathtext.fontset'] = 'cm'
mathtext_parser = MathTextParser("Bitmap")

# Define LaTeX math node:
class latex_math(nodes.General, nodes.Element):
    pass

def fontset_choice(arg):
    return directives.choice(arg, ['cm', 'stix', 'stixsans'])

options_spec = {'fontset': fontset_choice}

def math_role(role, rawtext, text, lineno, inliner,
              options={}, content=[]):
    i = rawtext.find('`')
    latex = rawtext[i+1:-1]
    node = latex_math(rawtext)
    node['latex'] = latex
    node['fontset'] = options.get('fontset', 'cm')
    return [node], []
math_role.options = options_spec

def math_directive(name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
    latex = ''.join(content)
    node = latex_math(block_text)
    node['latex'] = latex
    node['fontset'] = options.get('fontset', 'cm')
    return [node]

# This uses mathtext to render the expression
def latex2png(inline, latex, filename, fontset='cm'):
    if inline:
      latex = "$%s$" % latex
      orig_fontset = rcParams['mathtext.fontset']
      rcParams['mathtext.fontset'] = fontset
      if os.path.exists(filename):
          depth = mathtext_parser.get_depth(latex, dpi=100)
      else:
          try:
              depth = mathtext_parser.to_png(filename, latex, dpi=100)
          except:
              warnings.warn("Could not render math expression %s" % latex,
                          Warning)
              depth = 0
      rcParams['mathtext.fontset'] = orig_fontset
    else:
      if os.path.exists(filename):
          depth = mathtext_parser.get_depth(latex, dpi=100)
      else:
#         latex = r"\begin{displaymath}%s\end{displaymath}" % latex
          temptex = [r"\documentclass[12pt]{article}",r"\pagestyle{empty}",r"\begin{document}",r"\begin{displaymath}",latex,r"\end{displaymath}",r"\end{document}"]
#         temptex = [r"\begin{document}",r"\begin{displaymath}",latex,r"\end{displaymath}",r"\end{document}"]
          with open('__tmp.tex', 'w') as f:
            f.writelines(temptex)
          call(["latex","__tmp.tex"])
#         call(["latex2png","-m", "-d","100","__tmp.tex"])
          call(["dvipng","-D","100", "-o","__tmp.png","__tmp.dvi"])
          call(["pwd"])
          call(["convert","-crop","0x0", "-density","100x100","__tmp.png","__tmp.png"])
          call(["pwd"])
          call(["convert","-trim","__tmp.png","__tmp.png"])
          call(["pwd"])
          call(["convert","-crop","0x0+0+100", "__tmp.png","__tmp.png"])
          call(["mv", "__tmp.png",filename])
          depth=99
    sys.stdout.write("#")
    sys.stdout.flush()
    return depth

# LaTeX to HTML translation stuff:
def latex2html(node, source):
    inline = isinstance(node.parent, nodes.TextElement)
    latex = node['latex']
    name = 'math-%s' % md5(latex).hexdigest()[-10:]

    destdir = os.path.join(setup.app.builder.outdir, '_images', 'mathmpl')
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    dest = os.path.join(destdir, '%s.png' % name)
    path = os.path.join(setup.app.builder.imgpath, 'mathmpl')

    depth = latex2png(inline, latex, dest, node['fontset'])

    if inline:
        cls = ''
	br = ''
    else:
        cls = 'class="center" '
	br = '<br>'
    if inline and depth != 0:
        style = 'style="position: relative; bottom: -%dpx"' % (depth + 1)
    else:
        style = ''

    return '<img src="%s/%s.png" %s%s/>%s' % (path, name, cls, style, br)

def setup(app):
    setup.app = app

    app.add_node(latex_math)
    app.add_role('math', math_role)

    # Add visit/depart methods to HTML-Translator:
    def visit_latex_math_html(self, node):
        source = self.document.attributes['source']
        self.body.append(latex2html(node, source))
    def depart_latex_math_html(self, node):
        pass

    # Add visit/depart methods to LaTeX-Translator:
    def visit_latex_math_latex(self, node):
        inline = isinstance(node.parent, nodes.TextElement)
        if inline:
            self.body.append('$%s$' % node['latex'])
        else:
            self.body.extend(['\\begin{eqnarray}',
                              node['latex'],
                              '\\end{eqnarray}'])
    def depart_latex_math_latex(self, node):
        pass

    app.add_node(latex_math, html=(visit_latex_math_html,
                                   depart_latex_math_html))
    app.add_node(latex_math, latex=(visit_latex_math_latex,
                                    depart_latex_math_latex))
    app.add_role('math', math_role)
    app.add_directive('math', math_directive,
                      True, (0, 0, 0), **options_spec)
