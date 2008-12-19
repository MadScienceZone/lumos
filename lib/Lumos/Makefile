DIRLIST=Device GUI Network Extras

clean:
	rm -f *.pyc
	for dir in $(DIRLIST); do (cd $${dir} && $(MAKE) clean); done

distclean: clean
