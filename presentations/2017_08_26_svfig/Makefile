FILENAME=ga144nt

all: ${FILENAME}.pdf

${FILENAME}.pdf: ${FILENAME}.tex *.sty
	latexmk -pdf ${FILENAME}.tex

.PHONY: clean distclean show

clean:
	rm -f *.log *.nav *.snm *.toc *.aux *.out

distclean: clean
	rm -f ${FILENAME}.pdf

show: ${FILENAME}.pdf
	xdg-open $<
