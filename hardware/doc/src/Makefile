DOCS=lumos_dc_24_assembly.pdf lumos_dc_24_installation.pdf lumos_ssr_user_manual.pdf
BASENAMES=lumos_dc_24_assembly lumos_dc_24_installation lumos_ssr_user_manual
COMMONS=lumos_common.tex indent.sty acknowledgements.tex colophon.tex pinouts.tex dutycycle.tex 


all: $(DOCS)

#
# Quick reformat of document
#
lumos_dc_24_assembly.pdf: lumos_dc_24_assembly.tex $(COMMONS)
	pdflatex lumos_dc_24_assembly

lumos_dc_24_installation.pdf: lumos_dc_24_installation.tex $(COMMONS)
	pdflatex lumos_dc_24_installation

lumos_ssr_user_manual.pdf: lumos_ssr_user_manual.tex lumosasm.tex lumosctl.tex lumosupgrade.tex \
		acdutycycle.tex dcdutycycle.tex slices.tex timingchain.tex timingideal.tex \
		$(COMMONS)
	pdflatex lumos_ssr_user_manual

lumosasm.tex: ../../man/man1/lumosasm.1
	./man2latex ../../man/man1/lumosasm.1 lumosasm.tex

lumosupgrade.tex: ../../man/man1/lumosupgrade.1
	./man2latex ../../man/man1/lumosupgrade.1 lumosupgrade.tex

lumosctl.tex: ../../man/man1/lumosctl.1
	./man2latex ../../man/man1/lumosctl.1 lumosctl.tex

clean:
	rm -f *.aux *.idx *.ilg *.ind *.log *.synctex.gz *.toc

distclean: clean

pureclean: clean
	rm -rf $(DOCS)

#
# complete rebuild of document and indexes
#
rebuild: pureclean
	for basedoc in $(BASENAMES); do \
		echo "rebuilding $$basedoc"; \
		for pass in 1 2 3 4; do \
			echo "-- pass $$pass"; \
			pdflatex $$basedoc; \
			makeindex $$basedoc; \
		done; \
	done
