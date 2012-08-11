all: 48ssr_assembly_notes.pdf 48ssrctl.pdf

%.pdf : %.ps
	ps2pdf $< $@

%.pdf : %.1
	groff -man $< | ps2pdf - $@

%.ps : %.dvi
	dvips $<

%.dvi : %.tex
	latex $<
	latex $<
	latex $<

clean:
	rm -f *.aux *.dvi *.log *.ps *.toc

distclean: clean
	rm -f *.pdf
