clean:
	rm -rf build dist colusa.egg-info

bdist:
	python3 setup.py bdist bdist_wheel

upload:
	python3 -m twine upload dist/* --verbose

changelog:
	gitchangelog > CHANGELOG.md

bump_minor:
	bump2version minor

bump_major:
	bump2version major
