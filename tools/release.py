#!/usr/bin/env python3
"""
salt-ext-modules-vmware release script

The goal of this script is to simplify the release process, such that anyone
with the proper permissions should be able to run this script to generate a
release.

Release artifacts:
- wheel
- wheel.asc signature

When the wheel & sig file are tested & validated, then we want to tag the git revision and push it all to the places.

Would it be so wrong to update the version and commit before building? Or I suppose correctly we should ask.

"We're about to run tests for version X - would you like to continue?"

"""
import configparser
import contextlib
import logging
import os
import pathlib
import subprocess
import sys
import tempfile

DEBUG_FORCE = False
DEBUG_FORCE = True

log = logging.getLogger("extmod-release")
REPO_ROOT = pathlib.Path(__file__).parent.parent
TYPICAL_ENV = REPO_ROOT / "env" / "bin" / "python"
VENV_PYTHON = pathlib.Path(os.environ.get("VMWARE_VENV_PATH", TYPICAL_ENV))


def run_and_log_cmd(*cmd):
    log.debug("Running command %r", cmd)
    ret = subprocess.run(cmd, capture_output=True)
    log.debug(f"git status return code: %r", ret.returncode)
    log.debug(f"git status stdout: \n%s", ret.stdout.decode() or "<No stdout>")
    log.debug(f"git status stderr: \n%s", ret.stderr.decode() or "<No stderr>")
    return ret


@contextlib.contextmanager
def msg_wrap(msg):
    print(f"{msg}...", end="")
    sys.stdout.flush()
    try:
        yield
    except:
        print("FAIL")
        log.exception("Inner command failed")
    else:
        print("OK")


def do_it():  # Shia LeBeouf!
    pwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tempdir:
        dist_dir = pathlib.Path(tempdir) / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)

        os.chdir(tempdir)
        print(f"To see more information, run `tail -f {tempdir}/release.log`")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.FileHandler("release.log"))
        if sys.base_prefix != sys.prefix:
            exit(
                f"This python {sys.executable} is in a venv - deactivate and run using system python."
            )
        if not VENV_PYTHON.exists():
            exit(
                f"Python venv {VENV_PYTHON} does not exist. Set VMWARE_VENV_PATH environment variable, or run `python -m venv --prompt vmw-ext {TYPICAL_ENV.parent.parent}` to create a new virtualenv"
            )
        pypirc_path = pathlib.Path("~/.pypirc").expanduser()
        if not pypirc_path.exists():
            exit("No ~/.pypirc - will not be able to upload with twine")
        else:
            config = configparser.ConfigParser()
            config.read(pypirc_path)
            servers = [x for x in config["distutils"]["index-servers"].splitlines() if x]
            if "saltext_vmware" not in servers:
                exit("No saltext_vmware in pypirc, unable to do a prod deploy")
            elif "test_saltext_vmware" not in servers:
                exit("No test_saltext_vmware in pypirc, unable to do a test deploy")

        ret = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
        log.debug(f"git status return code: %r", ret.returncode)
        log.debug(f"git status stdout: \n%s", ret.stdout.decode() or "<No stdout>")
        log.debug(f"git status stderr: \n%s", ret.stderr.decode() or "<No stderr>")
        if ret.stdout and not DEBUG_FORCE:
            exit("You currently have changes in your repo. Stash or otherwise clear your changes.")

        with msg_wrap("Ensuring build/release deps are installed in venv"):
            run_and_log_cmd(
                str(VENV_PYTHON), "-m", "pip", "install", "-e", f"{REPO_ROOT}[dev,tests,release]"
            )

        with msg_wrap("Building the current package"):
            run_and_log_cmd(
                str(VENV_PYTHON),
                "-m",
                "pip",
                "wheel",
                "--wheel-dir",
                str(dist_dir),
                f"{REPO_ROOT}[dev,tests]",
            )

        test_virtualenv_path = pathlib.Path(tempdir) / "test_env"
        test_python = test_virtualenv_path / "bin" / "python"
        release_virtualenv_path = test_virtualenv_path.parent / "release_env"

        with msg_wrap("Creating a new virtualenv for testing"):
            run_and_log_cmd(
                sys.executable, "-m", "venv", "--prompt", "test_env", str(test_virtualenv_path)
            )

        with msg_wrap("Installing dev version of mod in test virtualenv"):
            run_and_log_cmd(
                str(test_python),
                "-m",
                "pip",
                "install",
                "saltext.vmware[dev,tests]",
                "--no-index",
                "--find-links",
                str(dist_dir),
            )

        with msg_wrap("Getting saltext version"):
            ret = run_and_log_cmd(str(test_python.parent / "salt"), "--versions-report")
            version = next(
                line
                for line in ret.stdout.decode().splitlines()
                if line.strip().startswith("saltext.vmware: ")
            ).partition(": ")[-1]

        with msg_wrap(f"Running tests for version {version}"):
            # run_and_log_cmd(str(test_python), '-m', 'nox', '-f', f'{REPO_ROOT}/noxfile.py', '-e', 'tests-3')
            ret = run_and_log_cmd(
                str(test_python),
                "-m",
                "nox",
                "-f",
                f"{REPO_ROOT}/noxfile.py",
                "-e",
                "tests-3",
                "--",
                "tests/unit",
            )
            if ret.returncode:
                raise Exception("No good!")

        input(f"enter to finish and cleanup - {tempdir}/release.log will be deleted")
        os.chdir(pwd)


def fake_it():
    import time

    keep_going = input("Building release version 22.01.06, continue? [y/N]: ")
    with msg_wrap("Generating changelog/release for commit"):
        time.sleep(0.5)

    with msg_wrap("Creating dev dir"):
        time.sleep(0.5)

    with msg_wrap("Creating venv for tests"):
        time.sleep(0.5)

    with msg_wrap("Building package wheels"):
        time.sleep(0.5)

    with msg_wrap("Installing saltext.vmware"):
        time.sleep(1)

    with msg_wrap("Running full test suite via nox"):
        time.sleep(1)

    with msg_wrap("Running tests via pytest"):
        time.sleep(5)

    keep_going = input("Tests are passing. Continue to sign package, deploy to dev pypi? [y/N]: ")

    with msg_wrap("Signing .whl"):
        time.sleep(0.5)

    with msg_wrap("Deploying build and signature to dev pypi"):
        time.sleep(2)

    print(
        "Deploy to dev pypi successful. See https://test.pypi.org/project/saltext.vmware/ to confirm."
    )

    keep_going = input("Deploy to prod pypi? [y/N]: ")

    with msg_wrap("Deploying build and signature to prod pypi"):
        time.sleep(2)

    with msg_wrap("Tagging release commit"):
        time.sleep(0.5)

    with msg_wrap("Pushing release tag to GitHub"):
        time.sleep(2)

    keep_artifacts = input("Release complete! Keep build artifacts around? [Y/n]: ")
    print("All done, good job!")


if __name__ == "__main__":
    # do_it()
    fake_it()
