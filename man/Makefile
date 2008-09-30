all: docs

docs: pdf/lcheck.1.pdf pdf/show.conf.5.pdf pdf/lumos-controller.4.pdf pdf/lumos-network.4.pdf pdf/show.conf.5.pdf pdf/lumos-sequence.5.pdf

clean:

distclean: clean
	rm -f pdf/*

pdf/lcheck.1.pdf: man1/lcheck.1
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-controller.4.pdf: man4/lumos-controller.4
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-network.4.pdf: man4/lumos-network.4
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/show.conf.5.pdf: man5/show.conf.5
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-sequence.5.pdf: man5/lumos-sequence.5
	groff -man $< | ps2pdf -sPaperSize=Letter - $@
