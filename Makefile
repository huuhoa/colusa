clean:
	rm -rf build dist colusa.egg-info

sdist:
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/* --verbose

changelog:
	gitchangelog > CHANGELOG.md


