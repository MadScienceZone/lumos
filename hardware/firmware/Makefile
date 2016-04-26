all:	listings pdf

hex:
	cp QuizShow.X/dist/default/production/QuizShow.X.production.hex QuizShow.hex

map:
	cp QuizShow.X/dist/default/production/QuizShow.X.production.map QuizShow.map
	./memorymap.py QuizShow.map QuizShow.desc QuizShow_map.txt

listings:
	cp QuizShow.X/build/default/production/_ext/1472/*.lst .

pdf: \
	flash_update.asm.pdf flash_update.inc.pdf \
	flash_update_bits.inc.pdf flash_update_user.inc.pdf \
	readerboard_32x16_ada.asm.pdf readerboard_32x16_ada.inc.pdf \
	readerboard_32x16_ada_bits.inc.pdf readerboard_32x16_ada_user.inc.pdf \
	lumos_8bit_escapes.inc.pdf lumos_config.inc.pdf lumos_init.asm.pdf \
	lumos_init.inc.pdf lumos_main.asm.pdf lumos_set_ssr.inc.pdf \
	lumos_ssr_state.inc.pdf qscc_bits.inc.pdf qscc_hook_120hz.asm.pdf \
	qscc_hook_5_6.asm.pdf qscc_hook_access_bank.inc.pdf \
	qscc_hook_global_commands.asm.pdf qscc_hook_io_setup.asm.pdf \
	qscc_hook_isr.asm.pdf qscc_hook_main_pins.inc.pdf \
	qscc_hook_s17.asm.pdf qscc_hook_s6_14.asm.pdf \
	qscc_hook_s9_priv_6.asm.pdf qscc_hook_s9_xa.asm.pdf \
	qscc_init.inc.pdf quizshow.inc.pdf quizshow_config.inc.pdf \
	quizshow_init.asm.pdf quizshow_main.asm.pdf \
	serial-io-bits.inc.pdf serial-io-user.inc.pdf \
	serial-io.asm.pdf serial-io.inc.pdf \
	lumos_init.lst.pdf lumos_main.lst.pdf quizshow_init.lst.pdf \
	quizshow_main.lst.pdf serial-io.lst.pdf QuizShow_map.txt.pdf

distclean:
	rm -f *.pdf

ENSCRIPTOPTS = -2 -G -H3 -j -M 11x17 -o - -r --highlight-bar-gray=0.90 --mark-wrapped-lines=arrow -L 87

%.inc.pdf: %.inc
	enscript $(ENSCRIPTOPTS) $< | ps2pdf - $@

%.asm.pdf: %.asm
	enscript $(ENSCRIPTOPTS) $< | ps2pdf - $@
	
%.lst.pdf: %.lst
	enscript $(ENSCRIPTOPTS) $< | ps2pdf - $@

%.txt.pdf: %.txt
	enscript $(ENSCRIPTOPTS) $< | ps2pdf - $@
