all: HACKING.pdf

clean:
	rm -f *.dvi *.log *.aux

distclean: clean
	rm -f *.pdf

HACKING.pdf: HACKING.dvi
	dvipdf HACKING

HACKING.dvi: HACKING.tex
	latex HACKING


