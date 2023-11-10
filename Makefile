CC:=latexmk
SRCDIR:=.
BIBDIR:=.
MEDIADIR:=./media
ODIR:=out
TARGET:=main
OPTIONS:=-pdf -shell-escape
TEX_FILES:=$(wildcard $(SRCDIR)/*.tex)
COMPILATION_FILES:=$(filter-out src/$(TARGET)_expanded.tex, $(TEX_FILES))


ZIP_TARGETS:= README.md $(BIBDIR)/cited.bib $(SRCDIR)/$(TARGET)_expanded.tex $(ODIR)/$(TARGET).pdf Figures/*

all:
	$(CC) $(OPTIONS) --output-directory=$(CURDIR)/$(ODIR) -cd $(CURDIR)/$(SRCDIR)/$(TARGET).tex

clean: clean_cite
	-rm -r $(ODIR)/*
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
