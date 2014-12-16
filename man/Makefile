all: builddocs

builddocs:  pdf/lcheck.pdf pdf/lplay.pdf pdf/lpower.pdf pdf/lsequence.pdf pdf/lumos.pdf pdf/ssrctl.pdf pdf/vixen2lumos.pdf pdf/lumos-controller.pdf pdf/lumos-network.pdf pdf/lumos-channel-map.pdf pdf/lumos-config.pdf pdf/lumos-sequence.pdf

clean:

distclean: clean
	rm -f pdf/*
	rm -f man?/*.[123456789]


#Manpages found in man1:
pdf/lcheck.pdf: man1/lcheck.1
	groff -man man1/lcheck.1 | ps2pdf -sPaperSize=Letter - $@

man1/lcheck.1: man1/lcheck.1.in
	./update_manpage < man1/lcheck.1.in > $@
pdf/lplay.pdf: man1/lplay.1
	groff -man man1/lplay.1 | ps2pdf -sPaperSize=Letter - $@

man1/lplay.1: man1/lplay.1.in
	./update_manpage < man1/lplay.1.in > $@
pdf/lpower.pdf: man1/lpower.1
	groff -man man1/lpower.1 | ps2pdf -sPaperSize=Letter - $@

man1/lpower.1: man1/lpower.1.in
	./update_manpage < man1/lpower.1.in > $@
pdf/lsequence.pdf: man1/lsequence.1
	groff -man man1/lsequence.1 | ps2pdf -sPaperSize=Letter - $@

man1/lsequence.1: man1/lsequence.1.in
	./update_manpage < man1/lsequence.1.in > $@
pdf/lumos.pdf: man1/lumos.1
	groff -man man1/lumos.1 | ps2pdf -sPaperSize=Letter - $@

man1/lumos.1: man1/lumos.1.in
	./update_manpage < man1/lumos.1.in > $@
pdf/ssrctl.pdf: man1/ssrctl.1
	groff -man man1/ssrctl.1 | ps2pdf -sPaperSize=Letter - $@

man1/ssrctl.1: man1/ssrctl.1.in
	./update_manpage < man1/ssrctl.1.in > $@
pdf/vixen2lumos.pdf: man1/vixen2lumos.1
	groff -man man1/vixen2lumos.1 | ps2pdf -sPaperSize=Letter - $@

man1/vixen2lumos.1: man1/vixen2lumos.1.in
	./update_manpage < man1/vixen2lumos.1.in > $@

#Manpages found in man4:
pdf/lumos-controller.pdf: man4/lumos-controller.4
	groff -man man4/lumos-controller.4 | ps2pdf -sPaperSize=Letter - $@

man4/lumos-controller.4: man4/lumos-controller.4.in
	./update_manpage < man4/lumos-controller.4.in > $@
pdf/lumos-network.pdf: man4/lumos-network.4
	groff -man man4/lumos-network.4 | ps2pdf -sPaperSize=Letter - $@

man4/lumos-network.4: man4/lumos-network.4.in
	./update_manpage < man4/lumos-network.4.in > $@

#Manpages found in man5:
pdf/lumos-channel-map.pdf: man5/lumos-channel-map.5
	groff -man man5/lumos-channel-map.5 | ps2pdf -sPaperSize=Letter - $@

man5/lumos-channel-map.5: man5/lumos-channel-map.5.in
	./update_manpage < man5/lumos-channel-map.5.in > $@
pdf/lumos-config.pdf: man5/lumos-config.5
	groff -man man5/lumos-config.5 | ps2pdf -sPaperSize=Letter - $@

man5/lumos-config.5: man5/lumos-config.5.in
	./update_manpage < man5/lumos-config.5.in > $@
pdf/lumos-sequence.pdf: man5/lumos-sequence.5
	groff -man man5/lumos-sequence.5 | ps2pdf -sPaperSize=Letter - $@

man5/lumos-sequence.5: man5/lumos-sequence.5.in
	./update_manpage < man5/lumos-sequence.5.in > $@
