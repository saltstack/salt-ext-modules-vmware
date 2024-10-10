# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""
noxfile
~~~~~~~

Nox configuration script
"""

# pylint: disable=missing-module-docstring,import-error,protected-access,missing-function-docstring
import datetime
import gzip
import json
import logging
import nox
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
from nox.command import CommandFailed
from nox.virtualenv import VirtualEnv

log = logging.getLogger("extvmware-release")


# fmt: off
if __name__ == "__main__":
    sys.stderr.write(
        "Do not execute this file directly. Use nox instead, it will know how to handle this file\n"
    )
    sys.stderr.flush()
    exit(1)
# fmt: on

# Nox options
#  Reuse existing virtualenvs
nox.options.reuse_existing_virtualenvs = True
#  Don't fail on missing interpreters
nox.options.error_on_missing_interpreters = False

# Python versions to test against
PYTHON_VERSIONS = ("3", "3.10")
# Be verbose when running under a CI context
CI_RUN = (
    os.environ.get("JENKINS_URL") or os.environ.get("CI") or os.environ.get("DRONE") is not None
)
PIP_INSTALL_SILENT = CI_RUN is False
SKIP_REQUIREMENTS_INSTALL = os.environ.get("SKIP_REQUIREMENTS_INSTALL", "0") == "1"
EXTRA_REQUIREMENTS_INSTALL = os.environ.get("EXTRA_REQUIREMENTS_INSTALL")

COVERAGE_REQUIREMENT = os.environ.get("COVERAGE_REQUIREMENT") or "coverage==7.5.1"
SALT_REQUIREMENT = os.environ.get("SALT_REQUIREMENT") or "salt>=3006"
if SALT_REQUIREMENT == "salt==master":
    SALT_REQUIREMENT = "git+https://github.com/saltstack/salt.git@master"

# Prevent Python from writing bytecode
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Global Path Definitions
REPO_ROOT = pathlib.Path(__file__).resolve().parent

TYPICAL_ENV = REPO_ROOT / "env" / "bin" / "python"
VENV_PYTHON = pathlib.Path(os.environ.get("VMWARE_VENV_PATH", TYPICAL_ENV))

# Change current directory to REPO_ROOT
os.chdir(str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
# Make sure the artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
CUR_TIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
RUNTESTS_LOGFILE = ARTIFACTS_DIR / f"runtests-{CUR_TIME}.log"
COVERAGE_REPORT_DB = REPO_ROOT / ".coverage"
COVERAGE_REPORT_PROJECT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-project.xml"
COVERAGE_REPORT_TESTS = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-tests.xml"
JUNIT_REPORT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "junit-report.xml"


def _get_session_python_version_info(session):
    try:
        version_info = session._runner._real_python_version_info
    except AttributeError:
        session_py_version = session.run_always(
            "python",
            "-c",
            'import sys; sys.stdout.write("{}.{}.{}".format(*sys.version_info))',
            silent=True,
            log=False,
        )
        version_info = tuple(int(part) for part in session_py_version.split(".") if part.isdigit())
        session._runner._real_python_version_info = version_info
    return version_info


def _get_pydir(session):
    version_info = _get_session_python_version_info(session)
    if version_info < (3, 10):
        session.error("Only Python >= 3.10 is supported")
    return f"py{version_info[0]}.{version_info[1]}"


def _install_requirements(
    session,
    *passed_requirements,  # pylint: disable=unused-argument
    install_coverage_requirements=True,
    install_test_requirements=True,
    install_source=False,
    install_salt=True,
    install_extras=None,
):
    install_extras = install_extras or []
    if SKIP_REQUIREMENTS_INSTALL is False:
        # Always have the wheel package installed
        session.install("--progress-bar=off", "wheel", silent=PIP_INSTALL_SILENT)
        if install_coverage_requirements:
            session.install("--progress-bar=off", COVERAGE_REQUIREMENT, silent=PIP_INSTALL_SILENT)

        if install_salt:
            session.install("--progress-bar=off", SALT_REQUIREMENT, silent=PIP_INSTALL_SILENT)

        if install_test_requirements and "tests" not in install_extras:
            install_extras.append("tests")

        if EXTRA_REQUIREMENTS_INSTALL:
            session.log(
                "Installing the following extra requirements because the "
                "EXTRA_REQUIREMENTS_INSTALL environment variable was set: "
                "EXTRA_REQUIREMENTS_INSTALL='%s'",
                EXTRA_REQUIREMENTS_INSTALL,
            )
            install_command = ["--progress-bar=off"]
            install_command += [req.strip() for req in EXTRA_REQUIREMENTS_INSTALL.split()]
            session.install(*install_command, silent=PIP_INSTALL_SILENT)

        if install_source:
            pkg = "."
            if install_extras:
                pkg += f"[{','.join(install_extras)}]"

            session.install("-e", pkg, silent=PIP_INSTALL_SILENT)


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    _install_requirements(session, install_source=True, install_extras=["tests"])

    sitecustomize_dir = session.run("salt-factories", "--coverage", silent=True, log=False)
    python_path_env_var = os.environ.get("PYTHONPATH") or None
    if python_path_env_var is None:
        python_path_env_var = sitecustomize_dir
    else:
        python_path_entries = python_path_env_var.split(os.pathsep)
        if sitecustomize_dir in python_path_entries:
            python_path_entries.remove(sitecustomize_dir)
        python_path_entries.insert(0, sitecustomize_dir)
        python_path_env_var = os.pathsep.join(python_path_entries)

    env = {
        # The updated python path so that sitecustomize is importable
        "PYTHONPATH": python_path_env_var,
        # The full path to the .coverage data file. Makes sure we always write
        # them to the same directory
        "COVERAGE_FILE": str(COVERAGE_REPORT_DB),
        # Instruct sub processes to also run under coverage
        "COVERAGE_PROCESS_START": str(REPO_ROOT / ".coveragerc"),
    }

    session.run("coverage", "erase")
    args = [
        "--rootdir",
        str(REPO_ROOT),
        f"--log-file={RUNTESTS_LOGFILE.relative_to(REPO_ROOT)}",
        "--log-file-level=debug",
        "--show-capture=no",
        f"--junitxml={JUNIT_REPORT}",
        "--showlocals",
        "-ra",
        "-s",
        "--cov",
        "src",
    ]
    if session._runner.global_config.forcecolor:
        args.append("--color=yes")
    if not session.posargs:
        args.append("tests/")
    else:
        for arg in session.posargs:
            if arg.startswith("--color") and args[0].startswith("--color"):
                args.pop(0)
            args.append(arg)
        for arg in session.posargs:
            if arg.startswith("-"):
                continue
            if arg.startswith(f"tests{os.sep}"):
                break
            try:
                pathlib.Path(arg).resolve().relative_to(REPO_ROOT / "tests")
                break
            except ValueError:
                continue
        else:
            args.append("tests/")

    session.run("pytest", *args, env=env)


class Tee:
    """
    Python class to mimic linux tee behaviour
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def write(self, buf):
        wrote = self._first.write(buf)
        self._first.flush()
        self._second.write(buf)
        self._second.flush()
        return wrote

    def fileno(self):
        return self._first.fileno()


def _lint(session, rcfile, flags, paths, tee_output=True):
    requirements_file = REPO_ROOT / "requirements" / _get_pydir(session) / "lint.txt"
    _install_requirements(session, "-r", str(requirements_file.relative_to(REPO_ROOT)))

    if tee_output:
        session.run("pylint", "--version")
        pylint_report_path = os.environ.get("PYLINT_REPORT")

    cmd_args = ["pylint", f"--rcfile={rcfile}"] + list(flags) + list(paths)

    src_path = str(REPO_ROOT / "src")
    python_path_env_var = os.environ.get("PYTHONPATH") or None
    if python_path_env_var is None:
        python_path_env_var = src_path
    else:
        python_path_entries = python_path_env_var.split(os.pathsep)
        if src_path in python_path_entries:
            python_path_entries.remove(src_path)
        python_path_entries.insert(0, src_path)
        python_path_env_var = os.pathsep.join(python_path_entries)

    env = {
        # The updated python path so that the project is importable without installing it
        "PYTHONPATH": python_path_env_var,
        "PYTHONUNBUFFERED": "1",
    }

    cmd_kwargs = {"env": env}

    if tee_output:
        stdout = tempfile.TemporaryFile(mode="w+b")
        cmd_kwargs["stdout"] = Tee(stdout, sys.__stdout__)

    try:
        session.run(*cmd_args, **cmd_kwargs)
    finally:
        if tee_output:
            stdout.seek(0)
            contents = stdout.read()
            if contents:
                contents = contents.decode("utf-8")
                sys.stdout.write(contents)
                sys.stdout.flush()
                if pylint_report_path:
                    # Write report
                    with open(pylint_report_path, "w") as wfh:
                        wfh.write(contents)
                    session.log("Report file written to %r", pylint_report_path)
            stdout.close()


def _lint_pre_commit(session, rcfile, flags, paths):
    if "VIRTUAL_ENV" not in os.environ:
        session.error(
            "This should be running from within a virtualenv and "
            "'VIRTUAL_ENV' was not found as an environment variable."
        )
    if "pre-commit" not in os.environ["VIRTUAL_ENV"]:
        session.error(
            "This should be running from within a pre-commit virtualenv and "
            f"'VIRTUAL_ENV'({os.environ['VIRTUAL_ENV']}) does not appear to be a pre-commit virtualenv."
        )

    # Let's patch nox to make it run inside the pre-commit virtualenv
    session._runner.venv = VirtualEnv(
        os.environ["VIRTUAL_ENV"],
        interpreter=session._runner.func.python,
        reuse_existing=True,
        venv=True,
    )
    _lint(session, rcfile, flags, paths, tee_output=False)


@nox.session(python="3")
def lint(session):
    """
    Run PyLint against the code and the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    session.notify(f"lint-code-{session.python}")
    session.notify(f"lint-tests-{session.python}")


@nox.session(python="3", name="lint-code")
def lint_code(session):
    """
    Run PyLint against the code. Set PYLINT_REPORT to a path to capture output.
    """
    flags = ["--disable=I"]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["setup.py", "noxfile.py", "src/"]
    _lint(session, ".pylintrc", flags, paths)


@nox.session(python="3", name="lint-tests")
def lint_tests(session):
    """
    Run PyLint against the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    flags = [
        "--disable=I,redefined-outer-name,missing-function-docstring,no-member,missing-module-docstring"
    ]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["tests/"]
    _lint(session, ".pylintrc", flags, paths)


@nox.session(python=False, name="lint-code-pre-commit")
def lint_code_pre_commit(session):
    """
    Run PyLint against the code. Set PYLINT_REPORT to a path to capture output.
    """
    flags = ["--disable=I"]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["setup.py", "noxfile.py", "src/"]
    _lint_pre_commit(session, ".pylintrc", flags, paths)


@nox.session(python=False, name="lint-tests-pre-commit")
def lint_tests_pre_commit(session):
    """
    Run PyLint against the code and the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    flags = [
        "--disable=I,redefined-outer-name,missing-function-docstring,no-member,missing-module-docstring",
    ]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["tests/"]
    _lint_pre_commit(session, ".pylintrc", flags, paths)


@nox.session(python="3")
def docs(session):
    """
    Build Docs
    """
    _install_requirements(
        session,
        install_coverage_requirements=False,
        install_test_requirements=False,
        install_source=True,
        install_extras=["docs"],
    )
    os.chdir("docs/")
    session.run("make", "clean", external=True)
    session.run("make", "linkcheck", "SPHINXOPTS=-Wn --keep-going", external=True)
    docs_coverage_file = os.path.join("_build", "html", "python.txt")
    if os.path.exists(docs_coverage_file):
        with open(docs_coverage_file) as rfh:  # pylint: disable=unspecified-encoding
            contents = rfh.readlines()[2:]
            if contents:
                session.error("\n" + "".join(contents))
    session.run("make", "html", "SPHINXOPTS=-Wn --keep-going", external=True)
    os.chdir(str(REPO_ROOT))


@nox.session(name="docs-dev", python="3")
@nox.parametrize("clean", [False, True])
def docs_dev(session, clean) -> None:
    """
    Build and serve the Sphinx HTML documentation, with live reloading on file changes, via sphinx-autobuild.

    Note: Only use this in INTERACTIVE DEVELOPMENT MODE. This SHOULD NOT be called
        in CI/CD pipelines, as it will hang.
    """
    _install_requirements(
        session,
        install_coverage_requirements=False,
        install_test_requirements=False,
        install_source=True,
        install_extras=["docs", "docsauto"],
    )

    # Launching LIVE reloading Sphinx session
    build_dir = Path("docs", "_build", "html")
    args = ["--watch", ".", "--open-browser", "docs", str(build_dir)]
    if clean and build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


@nox.session(name="docs-crosslink-info", python="3")
def docs_crosslink_info(session):
    """
    Report intersphinx cross links information
    """
    requirements_file = REPO_ROOT / "requirements" / _get_pydir(session) / "docs.txt"
    _install_requirements(
        session,
        "-r",
        str(requirements_file.relative_to(REPO_ROOT)),
        install_coverage_requirements=False,
        install_test_requirements=False,
        install_source=True,
    )
    os.chdir("docs/")
    intersphinx_mapping = json.loads(
        session.run(
            "python",
            "-c",
            "import json; import conf; print(json.dumps(conf.intersphinx_mapping))",
            silent=True,
            log=False,
        )
    )
    intersphinx_mapping_list = ", ".join(list(intersphinx_mapping))
    try:
        mapping_entry = intersphinx_mapping[session.posargs[0]]
    except IndexError:
        session.error(
            f"You need to pass at least one argument whose value must be one of: {intersphinx_mapping_list}"
        )
    except KeyError:
        session.error(f"Only acceptable values for first argument are: {intersphinx_mapping_list}")
    session.run(
        "python", "-m", "sphinx.ext.intersphinx", mapping_entry[0].rstrip("/") + "/objects.inv"
    )
    os.chdir(str(REPO_ROOT))


@nox.session(name="gen-api-docs", python="3")
def gen_api_docs(session):
    """
    Generate API Docs
    """
    _install_requirements(
        session,
        install_coverage_requirements=False,
        install_test_requirements=False,
        install_source=True,
        install_extras=["docs"],
    )
    try:
        shutil.rmtree("docs/ref")
    except FileNotFoundError:
        pass
    session.run(
        "sphinx-apidoc",
        "--implicit-namespaces",
        "--module-first",
        "-o",
        "docs/ref/",
        "src/saltext",
        "src/saltext/vmware/config/schemas",
    )


@nox.session(name="review", python="3")
def review(session):
    """
    Useful for code reviews - builds the docs locally and runs the full test suite.
    """
    session.notify("docs")
    session.notify(f"tests-{session.python}")


class Recompress:
    """
    Helper class to re-compress a ``.tag.gz`` file to make it reproducible.
    """

    def __init__(self, mtime):
        self.mtime = int(mtime)

    def tar_reset(self, tarinfo):
        """
        Reset user, group, mtime, and mode to create reproducible tar.
        """
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        tarinfo.mtime = self.mtime
        if tarinfo.type == tarfile.DIRTYPE:
            tarinfo.mode = 0o755
        else:
            tarinfo.mode = 0o644
        if tarinfo.pax_headers:
            raise ValueError(tarinfo.name, tarinfo.pax_headers)
        return tarinfo

    def recompress(self, targz):
        """
        Re-compress the passed path.
        """
        tempd = pathlib.Path(tempfile.mkdtemp()).resolve()
        d_src = tempd.joinpath("src")
        d_src.mkdir()
        d_tar = tempd.joinpath(targz.stem)
        d_targz = tempd.joinpath(targz.name)
        with tarfile.open(d_tar, "w|") as wfile:
            with tarfile.open(targz, "r:gz") as rfile:
                rfile.extractall(d_src)  # nosec
                extracted_dir = next(pathlib.Path(d_src).iterdir())
                for name in sorted(extracted_dir.rglob("*")):
                    wfile.add(
                        str(name),
                        filter=self.tar_reset,
                        recursive=False,
                        arcname=str(name.relative_to(d_src)),
                    )

        with open(d_tar, "rb") as rfh:
            with gzip.GzipFile(
                fileobj=open(d_targz, "wb"), mode="wb", filename="", mtime=self.mtime
            ) as gz:
                while True:
                    chunk = rfh.read(1024)
                    if not chunk:
                        break
                    gz.write(chunk)
        targz.unlink()
        shutil.move(str(d_targz), str(targz))


@nox.session(python="3")
def build(session):
    """
    Build source and binary distributions based off the current commit author date UNIX timestamp.

    The reason being, reproducible packages.

    .. code-block: shell

        git show -s --format=%at HEAD
    """
    shutil.rmtree("dist/", ignore_errors=True)
    session.install("--progress-bar=off", "-r", "requirements/build.txt", silent=PIP_INSTALL_SILENT)

    timestamp = session.run(
        "git",
        "show",
        "-s",
        "--format=%at",
        "HEAD",
        silent=True,
        log=False,
        stderr=None,
    ).strip()
    env = {"SOURCE_DATE_EPOCH": str(timestamp)}
    session.run(
        "python",
        "-m",
        "build",
        "--sdist",
        "--wheel",
        str(REPO_ROOT),
        env=env,
    )
    # Recreate sdist to be reproducible
    recompress = Recompress(timestamp)
    for targz in REPO_ROOT.joinpath("dist").glob("*.tar.gz"):
        session.log("Re-compressing %s...", targz.relative_to(REPO_ROOT))
        recompress.recompress(targz)

    sha256sum = shutil.which("sha256sum")
    if sha256sum:
        packages = [str(pkg.relative_to(REPO_ROOT)) for pkg in REPO_ROOT.joinpath("dist").iterdir()]
        session.run("sha256sum", *packages, external=True)
    session.run("python", "-m", "twine", "check", "dist/*")
