CC:=latexmk
MEDIADIR:=./media
TARGET:=main
BIBFILE:=predictive-microbiology-software
OPTIONS:=-pdf -shell-escape
TEX_FILES:=$(wildcard *.tex)
COMPILATION_FILES:=$(filter-out src/$(TARGET)_expanded.tex, $(TEX_FILES))

ZIP_TARGETS:= Makefile README.md $(BIBFILE)_cited.bib $(TARGET)_expanded.tex $(TARGET).pdf Figures/* svmult.cls

all:
	$(CC) $(OPTIONS) $(CURDIR)/$(TARGET).tex

clean: clean_cite clean_zip
	-rm -r *.aux
	-rm -r *.bbl
	-rm -r *.blg
	-rm -r *.fdb_latexmk
	-rm -r *.fls
	-rm -r *.log
	-rm -r *.out
	-rm -r *.pdf
	-rm -r *.pyg
	-rm -r _minted-main
	-rm -r $(TARGET)_expanded.tex

clean_cite:
	-rm -r $(BIBFILE)_cited.bib*

bibexport: all
	bibexport -r $(BIBFILE).bib -o $(BIBFILE)_cited.bib $(TARGET).aux

latexpand:
	latexpand $(TARGET).tex > $(TARGET)_expanded.tex

fresh: clean clean_cite all

examine:
	pplatex -i $(TARGET).log

wordcount:
	texcount $(COMPILATION_FILES)

citecount: clean_cite bibexport
	cat $(BIBFILE)_cited.bib | grep -o ^@ | wc -l

zip: all bibexport latexpand
	zip $(TARGET) $(ZIP_TARGETS)
	printf "@ $(TARGET)_expanded.tex\n@=$(TARGET).tex" | zipnote -w $(TARGET).zip
	
	printf "@ $(BIBFILE)_cited.bib\n@=$(BIBFILE).bib\n" | zipnote -w $(TARGET).zip
	printf "@ $(TARGET)_expanded.tex\n@=$(TARGET).tex\n" | zipnote -w $(TARGET).zip

clean_zip:
	-rm -r $(TARGET).zip
