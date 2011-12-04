all: builddocs

builddocs:  pdf/lcheck.pdf pdf/lplay.pdf pdf/lumos.pdf pdf/vixen2lumos.pdf pdf/lumos-controller.pdf pdf/lumos-network.pdf pdf/lumos-channel-map.pdf pdf/lumos-config.pdf pdf/lumos-sequence.pdf

clean:

distclean: clean
	rm -f pdf/*


#Manpages found in man1:
pdf/lcheck.pdf: man1/lcheck.1
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lplay.pdf: man1/lplay.1
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos.pdf: man1/lumos.1
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/vixen2lumos.pdf: man1/vixen2lumos.1
	groff -man $< | ps2pdf -sPaperSize=Letter - $@


#Manpages found in man4:
pdf/lumos-controller.pdf: man4/lumos-controller.4
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-network.pdf: man4/lumos-network.4
	groff -man $< | ps2pdf -sPaperSize=Letter - $@


#Manpages found in man5:
pdf/lumos-channel-map.pdf: man5/lumos-channel-map.5
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-config.pdf: man5/lumos-config.5
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

pdf/lumos-sequence.pdf: man5/lumos-sequence.5
	groff -man $< | ps2pdf -sPaperSize=Letter - $@

