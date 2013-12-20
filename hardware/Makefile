RELEASE=3.0
RELEASEDC=1.0.9
DIRLIST=bin doc doc/src

all: builddocs buildasm buildpcb

builddocs:
	cp man/man1/*.1 doc/src
	(cd doc/src && $(MAKE) rebuild && cp -v *.pdf ..)

buildasm:
	rm -rf LumosROM-$(RELEASE)
	mkdir LumosROM-$(RELEASE)
	cp firmware/*.inc firmware/*.asm LumosROM-$(RELEASE)
	cp firmware/dist/$(RELEASE)/LumosROM-$(RELEASE)-standalone.hex LumosROM-$(RELEASE)

buildpcb:
	rm -rf Lumos24DC-$(RELEASEDC)
	mkdir Lumos24DC-$(RELEASEDC)
	cp firmware/dist/$(RELEASE)/LumosROM-$(RELEASE)-standalone.hex Lumos24DC-$(RELEASEDC)/Lumos24DC_Firmware-$(RELEASE).hex
	cp pcb/*.pdf pcb/*.gbr pcb/*.cnc pcb/*.png Lumos24DC-$(RELEASEDC)
	cp schematics/*.pdf Lumos24DC-$(RELEASEDC)

test:
	(cd Test && $(MAKE))

clean:
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) clean); done
	rm -f setup-Windows.py

distclean: clean
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) distclean); done
	rm -rf dist_bin
	rm -f bin/*.pyc

dist: distclean builddocs buildasm buildpcb
	(mkdir -p dist_bin && cd bin && for file in *; do sed -e 's/@@RELEASE@@/$(RELEASE)/g' -e 's/^#@@REL@@//' < $$file > ../dist_bin/$$file; done)
	tar cvfz dist/Lumos24DC-$(RELEASEDC).tar.gz Lumos24DC-$(RELEASEDC)
	tar cvfz dist/LumosROM-$(RELEASE).tar.gz 
	rm -rf Lumos24DC-$(RELEASEDC) LumosROM-$(RELEASE)
