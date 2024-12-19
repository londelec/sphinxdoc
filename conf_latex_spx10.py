# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = u'a4'


# The font size ('10pt', '11pt' or '12pt').
latex_font_size = u'10pt'

# Additional files to copy to latex output directory.
latex_additional_files = ["_images/logo.pdf"]

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [(master_doc, 'output.tex', project, u'', 'manual')]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = '_images/logo.pdf'

# If true, add page references after internal references. This is very useful for printed copies of the manual. Default is False.
#latex_show_pagerefs = True

# If true, show URL addresses after external links.
#latex_show_urls = False

# A dictionary that contains LaTeX snippets that override those Sphinx usually
# puts into the generated .tex files.
latex_elements = {
    'preamble':

        r'''
        \usepackage{array}
        \usepackage{tikz}
        \usepackage{xcolor}
        \usepackage{colortbl}
        \usepackage{etoolbox}
        \usepackage[strict]{changepage}
        \usepackage{soul}
        \usepackage{listings}

        % manual: http://mirror.datacenter.by/pub/mirrors/CTAN/macros/latex/contrib/caption/caption-eng.pdf
        \usepackage[nooneline,labelfont=bf,textfont=bf,labelsep=space]{caption}
        \captionsetup[table]{skip=0pt}
        \captionsetup[figure]{justification=centerfirst}

        % define colors
        \definecolor{tablebordercolor}{HTML}{DDDDDD}
        \definecolor{tableheadercolor}{HTML}{EEEEEE}

        \definecolor{color@tip}{HTML}{6B9946}
        \definecolor{color@note}{HTML}{5BC0DE}
        \definecolor{color@important}{HTML}{D9534F}
        \definecolor{color@attention}{HTML}{478DA2}

        \definecolor{coverbacground}{HTML}{383838}
        \definecolor{legreen}{HTML}{A9D046}
        \definecolor{xmlcolor}{HTML}{355F7C}
        \definecolor{monospacebg}{HTML}{E0E0E0}

        % change default font
        \renewcommand*{\familydefault}{\sfdefault}

        % change page layout
        \advance\textwidth by 0.8in
        \setlength{\marginparwidth}{20pt}
        \addtolength{\oddsidemargin}{-0.4in}
        \addtolength{\evensidemargin}{-0.4in}

        % redefine header and footer
        \makeatletter
            \fancypagestyle{normal}{
                \fancyhf{}
                \fancyfoot[LE,RO]{{\py@HeaderFamily\thepage}}
                \fancyfoot[LO,RE]{{\py@HeaderFamily \@title\space\version}}
                \fancyhead[LO]{{\py@HeaderFamily\nouppercase{\rightmark}}}
                \fancyhead[RE]{{\py@HeaderFamily\nouppercase{\leftmark}}}

                \renewcommand{\headrulewidth}{0.4pt}
                \renewcommand{\footrulewidth}{0.4pt}
                % define chaptermark with \@chappos when \@chappos is available for Japanese
                \ifx\@chappos\undefined\else
                    \def\chaptermark##1{\markboth{\@chapapp\space\thechapter\space\@chappos\space ##1}{}}
                \fi
            }
        \makeatother

        % section placement
        \newcommand{\sectionbreak}{\clearpage}
        \pretocmd{\section}{%
            \ifnum\value{section}=0
            \else
                \clearpage
            \fi
        }{}{}

        \pretocmd{\subsection}{%
            \clearpage
        }{}{}

        % redefine title page
        \AtBeginDocument{%
           \renewcommand{\releasename}{Version}
        }

        % insert there to override title page
        \makeatletter

        \renewcommand{\maketitle}{%
          \begin{titlepage}%
            \let\footnotesize\small
            \let\footnoterule\relax
            \rule{\textwidth}{1pt}%
            \ifsphinxpdfoutput
              \begingroup
              \def\\{, }
              \def\and{and }
              \pdfinfo{
                /Author (\@author)
                /Title (\@title)
              }
              \endgroup
            \fi
            \begin{flushright}%
              \sphinxlogo%
              {\rm\Huge\py@HeaderFamily \@title \par}%
              {\em\LARGE\py@HeaderFamily \py@release\releaseinfo \par}
              \vfill
              {\LARGE\py@HeaderFamily
                \begin{tabular}[t]{c}
                  \@author
                \end{tabular}
                \par}
              \vfill\vfill
              {\large
               \@date \par
               %\vfill
               %\py@authoraddress \par
              }%
            \end{flushright}%\par
            %\@thanks
          \end{titlepage}%
          \cleardoublepage%
          \setcounter{footnote}{0}%
          \let\thanks\relax\let\maketitle\relax
        }
        \makeatother

        \addto\captionsenglish{\renewcommand{\chaptername}{Section}}
        \setlength{\LTleft}{0pt}
        \setlength\LTright{0pt}

        \def\arraystretch{1.5}%  1 is the default
        \newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
        \newcolumntype{S}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
        \newcolumntype{E}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

        % Colors
        % from sphinx.sty
        % Redefine these colors to your liking in the preamble.
        \definecolor{TitleColor}{HTML}{000000}
        \definecolor{InnerLinkColor}{HTML}{000000}
        \definecolor{OuterLinkColor}{HTML}{2A6496}

        % Redefine these colors to something not white if you want to have colored
        % background and border for code examples.
        \definecolor{VerbatimColor}{HTML}{F5F5F5}
        \definecolor{VerbatimBorderColor}{HTML}{CCCCCC}

        % Underline links
        \setul{2.0pt}{.5pt}
        \setulcolor{InnerLinkColor}

        % link styles
        \newcommand{\docutilsrolexmlattr}{\color{xmlcolor}\itshape}
        \newcommand{\docutilsrolexmlelem}{\color{xmlcolor}\itshape}
        \newcommand{\docutilsrolexmlgroup}{\color{xmlcolor}\itshape}
        \newcommand{\docutilsroledocref}{\setulcolor{black}\normalfont\color{TitleColor}\bfseries\ul}
        \newcommand{\docutilsrolebitref}{\setulcolor{black}\color{TitleColor}\itshape\ul}

	% XML only styles
        \newcommand{\docutilsrolexmlstyle}{\color{xmlcolor}\itshape}
        \newcommand{\docutilsrolexmllegacy}{\color{xmlcolor}\itshape}

        \AtBeginDocument{%
           % This is required to underline links created from :numref:
           % because \ul{Table \ref{xxx}} doesn't work
           \newcommand{\numhyperref[2]}{%
            \hyperref[#1]{\color{TitleColor}\bfseries\underline{#2}}%
           }
        }

        % title styles
        \titleformat{\section}{\color{black}\Large\bfseries\sffamily}{\color{black}\thesection}{1em}{}
        \titleformat{\subsection}{\color{black}\large\bfseries\sffamily}{\color{black}\thesubsection}{1em}{}
        \titleformat{\subsubsection}{\color{black}\normalsize\bfseries\sffamily}{\color{black}\thesubsubsection}{1em}{}

        % table styles
        \arrayrulecolor{tablebordercolor}
        \setlength{\tabcolsep}{4pt}

        % notices (tip, note, warning)
        \makeatletter
        \newenvironment{noticesidebar}[2][\hsize]
        {%
            \def\FrameCommand
            {%
                {\color{color@#2}\vrule width 3pt}%
                \hspace{0pt}%must no space.
                \fboxsep=\FrameSep\fcolorbox{color@#2}{white}%
            }%
            \MakeFramed{\hsize#1\advance\hsize-\width\FrameRestore}%
        }
        {\endMakeFramed}

        \newenvironment{admonitionbox}[2]{
         \begin{lrbox}{\@tempboxa}\begin{minipage}{\textwidth}
         \textcolor{color@#1}{\strong{#2}}\\
        }{
         \end{minipage}\end{lrbox}
         {\usebox{\@tempboxa}}
        }

        \renewenvironment{notice}[2]{
         \begin{noticesidebar}{#1}\begin{admonitionbox}{#1}{#2}
        }{
         \end{admonitionbox}{}\end{noticesidebar}
        }
        \makeatother

        % text highlight styles
        \newcommand{\docutilsroleinlinetip}{\color{color@tip}}
        \newcommand{\docutilsroleinlineimportant}{\color{color@important}}
        \newcommand{\docutilsroleinlineattention}{\color{color@attention}}
        \newcommand{\docutilsroleleubold}{\setulcolor{black}\color{TitleColor}\bfseries\ul}
        \newcommand{\docutilsrolelemonobgtext}{\ttfamily\colorbox{monospacebg}}

        % Override DUspan command defined in sphinx.sty. Argument #2 must immediately follow docutilsrole#1
        \renewcommand*{\DUspan}[2]{%
         \ifcsname docutilsrole#1\endcsname
          {\csname docutilsrole#1\endcsname{#2}}%
         \else
          {#2}%
         \fi
        }

        % decrease verbatim width (code examples container width)
        \renewcommand{\Verbatim}[1][1]{%
          % list starts new par, but we don't want it to be set apart vertically
          \bgroup\parskip=0pt%
          \smallskip%
          % The list environement is needed to control perfectly the vertical space.
          \list{}{%
          \setlength\parskip{0pt}%
          \setlength\itemsep{0ex}%
          \setlength\topsep{0ex}%
          \setlength\partopsep{0pt}%
          \setlength\leftmargin{0pt}%
          }%
          \item\MakeFramed {\advance\hsize-\width\FrameRestore}%
             \small%
            \OriginalVerbatim[#1,samepage=true,fontsize=\footnotesize]%
        }

        % listings used instead of verbatim
        \lstset{
          breaklines=true,
          backgroundcolor=\color{VerbatimColor},
          frame=single,
          basicstyle=\fontsize{8}{10}\ttfamily}

        \setcounter{tocdepth}{2}
        ''',

    'babel': '\\usepackage[english]{babel}'
}

if 'latex_options' in locals() or 'latex_options' in globals():
    latex_elements['preamble'] += latex_options.get('preamble', '')
