generate:
	python3 main.py

html:
	cd the-morning-paper && asciidoctor index.asciidoc -d book -b html5 -o index.html

epub:
	cd the-morning-paper && asciidoctor-epub3 index.asciidoc -d book -D output

kf8:
	cd the-morning-paper && asciidoctor-epub3 index.asciidoc -d book -D output -a ebook-format=kf8

