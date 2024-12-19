# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS	= -a
SPHINXBUILD	= sphinx-build
PAPER		=
BUILDDIR	= build
TEMPDIR	= /tmp/sphinx

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS)

ifneq ($(shell python -c "help('modules')" 2>/dev/null | grep -o sphinx),)
PYTHON = python
else ifneq ($(shell python3 -c "help('modules')" 2>/dev/null | grep -o sphinx),)
PYTHON = python3
endif

.PHONY: help clean singlehtml singlehtml_internal latexpdf latexpdf_internal python_check confproj

help: python_check
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"

clean:
	-rm -rf $(BUILDDIR)/*

singlehtml: confproj
	$(CONFIGDIR)/prebuild_sphinx.py $(TEMPDIR) singlehtml
	$(SPHINXBUILD) -b singlehtml -t singlehtml -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(TEMPDIR) $(BUILDDIR)/singlehtml
	$(PYTHON) $(CONFIGDIR)/postbuild_html.py $(BUILDDIR)/$@ $(TARGET) $(TEMPDIR)
	-rm -rf $(TEMPDIR)

	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

singlehtml_internal: confproj
	$(CONFIGDIR)/prebuild_sphinx.py $(TEMPDIR) internal
	$(SPHINXBUILD) -b singlehtml -t singlehtml -t internal -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(TEMPDIR) $(BUILDDIR)/internal_singlehtml
	$(PYTHON) $(CONFIGDIR)/postbuild_html.py $(BUILDDIR)/internal_singlehtml $(TARGET) $(TEMPDIR)
	-rm -rf $(TEMPDIR)

	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/internal_singlehtml."

latexpdf: confproj
	$(CONFIGDIR)/prebuild_sphinx.py $(TEMPDIR) latexpdf
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(TEMPDIR) $(BUILDDIR)/latex
	-rm -rf $(TEMPDIR)
	$(PYTHON) $(CONFIGDIR)/prebuild_latex.py $(BUILDDIR)/latex/output.tex

	@echo "Running LaTeX files through pdflatex..."
	make -C $(BUILDDIR)/latex all-pdf
	$(CONFIGDIR)/postbuild_latex.py $(BUILDDIR)/latex $(TARGET)

	@echo
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

latexpdf_internal: confproj
	$(CONFIGDIR)/prebuild_sphinx.py $(TEMPDIR) internal
	$(SPHINXBUILD) -b latex -t internal $(ALLSPHINXOPTS) $(TEMPDIR) $(BUILDDIR)/internal_latex
	-rm -rf $(TEMPDIR)
	$(PYTHON) $(CONFIGDIR)/prebuild_latex.py $(BUILDDIR)/internal_latex/output.tex

	@echo "Running LaTeX files through pdflatex..."
	make -C $(BUILDDIR)/internal_latex all-pdf
	$(CONFIGDIR)/postbuild_latex.py $(BUILDDIR)/internal_latex $(TARGET)

	@echo
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/internal_latex."

python_check:
ifdef PYTHON
	@echo "Using $(PYTHON)"
else
	$(error Error: python doesn't have sphinx)
endif

confproj: python_check
	-rm -rf $(TEMPDIR)
	cp -r source $(TEMPDIR)
	$(PYTHON) $(CONFIGDIR)/prebuild_project.py $(TEMPDIR)
