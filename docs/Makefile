all: builddocs

builddocs: HACKING.pdf lumos-user-guide.pdf

clean:
	rm -f *.dvi *.log *.aux *.toc

distclean: clean
	rm -f *.pdf

lumos-user-guide.pdf: lumos-user-guide.dvi
	dvipdf lumos-user-guide

lumos-user-guide.dvi: lumos-user-guide.tex
	latex lumos-user-guide
	latex lumos-user-guide
	latex lumos-user-guide

HACKING.pdf: HACKING.dvi
	dvipdf HACKING

HACKING.dvi: HACKING.tex
	latex HACKING


