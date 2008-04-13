all: runtests docs

docs: pdf/lcheck.pdf pdf/show.conf.pdf pdf/lumos-controller.pdf pdf/lumos-network.pdf

runtests:
	Test/texttestrunner

clean:
	rm -f *.pyc bin/*.pyc lib/*.pyc Test/*.pyc

distclean: clean
	rm -f pdf/*

pdf/lcheck.pdf: man/man1/lcheck.1
	groff -man $< | ps2pdf - $@

pdf/show.conf.pdf: man/man5/show.conf.5
	groff -man $< | ps2pdf - $@

pdf/lumos-controller.pdf: man/man4/lumos-controller.4
	groff -man $< | ps2pdf - $@

pdf/lumos-network.pdf: man/man4/lumos-network.4
	groff -man $< | ps2pdf - $@
