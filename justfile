default:
    just --list

PY3:='./venv/bin/python3'

# Project Development

build-docs:
	{{ PY3 }} -m sphinx -b html ./docs ./docs/_build/html

serve-docs reload = "true": ## Serve the documentation with optional auto-reload (reload=true|false)
	{{ PY3 }} -m pip install --quiet sphinx-autobuild
	@if [ "{{reload}}" = "true" ]; then \
		echo "Serving with auto-reload enabled..."; \
		{{ PY3 }} -m sphinx-autobuild -b html ./docs ./docs/_build/html; \
	else \
		cd docs/_build/html && {{ PY3 }} -m http.server 8000 --bind 127.0.0.1; \
	fi
