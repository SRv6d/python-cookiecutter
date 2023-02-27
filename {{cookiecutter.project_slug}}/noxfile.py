import os

import nox
from nox_poetry import session

CI = bool(os.getenv("CI"))
PYTHON = "{{ cookiecutter._python_version_specs[cookiecutter.python_version]['versions'] | join(', ') }}".split(", ") if not CI else None
LINT_LOCATIONS = "src", "tests", "noxfile.py"
SESSIONS = "ruff", "black", "mypy", "tryceratops", "pytest_unit"

nox.options.sessions = SESSIONS


@session(python=PYTHON)
def ruff(session) -> None:
    """Lint code using ruff."""
    session.install("ruff")

    if session.posargs:
        session.run("ruff", *session.posargs, *LINT_LOCATIONS)
    else:
        session.run("ruff", *LINT_LOCATIONS)


@session(python=PYTHON)
def black(session) -> None:
    """Check if style adheres to black."""
    session.install("black")
    session.run("black", "--check", *LINT_LOCATIONS)


@session(python=PYTHON)
def black_format(session) -> None:
    """Format code using black."""
    session.install("black")
    session.run("black", *LINT_LOCATIONS)


@session(python=PYTHON)
def mypy(session) -> None:
    """Static type checking using mypy."""
    session.run("poetry", "install", external=True)
    session.run("mypy", *LINT_LOCATIONS)


@session(python=PYTHON)
def tryceratops(session) -> None:
    """Exception Style linting using tryceratops."""
    session.install("tryceratops")
    session.run("tryceratops", *LINT_LOCATIONS)


@session(python=PYTHON)
def pytest_unit(session) -> None:
    """Run unit tests using pytest."""
    session.run("poetry", "install", "--only=main,test", external=True)
    session.run("pytest", "--cov", "tests/unit")


@session(python=PYTHON)
def pytest_integration(session) -> None:
    """Run integration tests using pytest."""
    session.run("poetry", "install", "--only=main,test", external=True)
    session.run("pytest", "--cov", "tests/integration")


@session(python=PYTHON)
def pytest_e2e(session) -> None:
    """Run e2e tests using pytest."""
    session.run("poetry", "install", "--only=main,test", external=True)
    session.run("pytest", "--cov", "tests/e2e")


@session(python=PYTHON)
def safety(session) -> None:
    """Scan dependencies for known security vulnerabilities using safety."""
    session.install("safety")
    requirements_file = session.poetry.export_requirements()
    session.run("safety", "check", f"--file={requirements_file}", "--full-report")


@nox.session(python=PYTHON)
def codecov(session) -> None:
    """Upload codecov coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", "-f", "coverage.xml")
