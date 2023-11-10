CC:=latexmk
SRCDIR:=.
BIBDIR:=.
MEDIADIR:=./media
ODIR:=.
TARGET:=main
OPTIONS:=-pdf -shell-escape
TEX_FILES:=$(wildcard $(SRCDIR)/*.tex)
COMPILATION_FILES:=$(filter-out src/$(TARGET)_expanded.tex, $(TEX_FILES))


ZIP_TARGETS:= Makefile README.md $(BIBDIR)/cited.bib $(SRCDIR)/$(TARGET)_expanded.tex $(ODIR)/$(TARGET).pdf Figures/* svmult.cls

all:
	$(CC) $(OPTIONS) --output-directory=$(CURDIR)/$(ODIR) -cd $(CURDIR)/$(SRCDIR)/$(TARGET).tex

clean: clean_cite
	-rm -r $(ODIR)/*.aux
	-rm -r $(ODIR)/*.bbl
	-rm -r $(ODIR)/*.blg
	-rm -r $(ODIR)/*.fdb_latexmk
	-rm -r $(ODIR)/*.fls
	-rm -r $(ODIR)/*.log
	-rm -r $(ODIR)/*.out
	-rm -r $(ODIR)/*.pdf
	-rm -r $(ODIR)/*.pyg
	-rm -r $(ODIR)/_minted-main
	-rm $(SRCDIR)/$(TARGET)_expanded.tex
	-rm $(CURDIR)/release.zip

clean_cite:
	-rm -r $(BIBDIR)/cited.bib*

bibexport: all
	bibexport -r $(BIBDIR)/Paper-ode-integrate.bib -o $(BIBDIR)/cited.bib $(ODIR)/$(TARGET).aux

latexpand:
	cd $(SRCDIR); latexpand $(TARGET).tex > $(TARGET)_expanded.tex

fresh: clean clean_cite all

examine:
	pplatex -i $(ODIR)/$(TARGET).log

wordcount:
	texcount $(COMPILATION_FILES)

citecount: clean_cite bibexport
	cat $(BIBDIR)/cited.bib | grep -o ^@ | wc -l

zip: all bibexport latexpand
	zip $(TARGET) $(ZIP_TARGETS)
