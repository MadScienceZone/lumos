RELEASE=3.0
DIRLIST=bin doc doc/src

all: builddocs

builddocs:
	cp man/man1/*.1 docs/src
	(cd docs/src && $(MAKE) rebuild && cp -v *.pdf ..)

test:
	(cd Test && $(MAKE))

clean:
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) clean); done
	rm -f setup-Windows.py

distclean: clean
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) distclean); done
	rm -rf dist_bin
	rm -f bin/*.pyc

dist: distclean builddocs
	(mkdir -p dist_bin && cd bin && for file in *; do sed -e 's/@@RELEASE@@/$(RELEASE)/g' -e 's/^#@@REL@@//' < $$file > ../dist_bin/$$file; done)
	./setup.py sdist --formats=gztar,zip
