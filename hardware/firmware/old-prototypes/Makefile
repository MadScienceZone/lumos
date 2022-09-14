MASTER=48ctl-master
SLAVE=48ctl-slave-877
SL777=48ctl-slave-777

all: $(MASTER).pdf $(SLAVE).pdf $(SL777).pdf

%.pdf : %.lst
	enscript -M 17x11 -r -h -2 -B -H3 -j -f Courier7 -p - --highlight-bar-gray=.85 $< | ps2pdf - $@

clean:

distclean: clean
	rm *.pdf
