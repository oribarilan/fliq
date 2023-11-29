default:
    just --list


alias tc := test-coverage
alias t := test
alias c := check

# one time setup for env
setup:
    pip install -r requirements-dev.txt
    pip install -e .

# execute tests with coverage
test-coverage:
    coverage run --omit 'fliq/tests/*','*/__pycache__/*','examples' -m pytest --ignore=examples
    coverage report -m --fail-under=95

# execute tests
test:
    pytest --ignore=examples

# test docs
test-docs:
    python -m doctest fliq/query.py

# execute linting utils
lint:
    ruff .

# execute quality utils
quality:
    mypy fliq

# execute all code checks (linting and quality)
check:
    just test-docs
    just lint
    just quality
    just test-coverage

# test and build docs
doc:
    python -m doctest fliq/query.py
    python scripts/gen_docs.py
    python scripts/execute_doc_files.py
    mkdocs build

# test, build and run docs server
doc-serve:
    just doc
    mkdocs serve

# run all checks, test and build docs
prep:
    just check
    just doc

ori:
    python -m doctest README.md