generate:
	python3 main.py

html:
	asciidoctor index.asciidoc -d book -b html5 -o index.html

epub:
	asciidoctor-epub3 index.asciidoc -d book -D output

kf8:
	asciidoctor-epub3 index.asciidoc -d book -D output -a ebook-format=kf8

