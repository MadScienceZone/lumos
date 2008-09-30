DIRLIST=docs man Test lib/Lumos

all: docs test

docs: 
	(cd man && $(MAKE))
	(cd docs && $(MAKE))

test:
	(cd Test && $(MAKE))

clean:
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) clean); done

distclean: clean
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) distclean); done
