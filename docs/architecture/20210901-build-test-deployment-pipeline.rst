2021-09-01 Build/Test/Deployment Pipeline
=========================================

Status
------

Approved/Development

Context
-------

The motivations behind our CI/CD pipeline are:

* quick tests
* full confidence on deploys
* "nightly" builds

We want our tests to run as fast as reasonably possible. At the current time,
Django has a unit test suite that runs over 150,000 tests in about 30 minutes.
This is an entirely reasonable amount of time to wait for tests to run. Much
longer and the feedback cycle takes much too long. For a project the size of
Django, 30 minutes is a reasonable amount of time. For this module, our PR
checks should take no longer than 15 minutes.

Of course the reason that we want tests in the first place is that
well-written, meaningful tests allow us to deploy the most reasonably reliable
software we can. Obviously perfect reliability is unattainable, but there are a
lot of things that we can do to improve reliability for a reasonable amount of
effort.

We also want to provide users the ability to continually check our development
against their own environments, by producing "nightly" builds. The quotation
marks are there because maybe it's not nightly, maybe it's weekly. Or some
other sensible, frequent period of releases. Nightly would be fine if we need
to build that often.

Murphy's Law
------------

> Anything that can go wrong will go wrong.

This principle is baked into the design of the pipeline. At each step it should
fail safe and be *possible* to re-start at that step of the pipeline. That way,
if something fails for an external reason (power outage, DNS failure, gamma
rays), we will be able to resume where we left off, instead of having to do
something like create a new PR to launch the whole process again. As long as
successful artifacts exist from the previous step in the pipeline, each step
should be able to be re-started.

Pipline Overview
----------------

.. ::

                    +-----------------------------------------------+
                    |   input: local code/doc changes               |
                    |                                               |
                    |       Local pre-commit hooks                  | <----------------------,
                    |                                               |                         |
                    |   output: new code locally                    |                         |
                    +----------------------+------------------------+                         |
                                           |                                                  |
                                           |                                                  |
                                           V                                                  |
                    +-----------------------------------------------+                         |
                    |   input: local code                           |                         |
                    |                                               |                       ./|
                    |       Local intgration/unit test runs*        +--[ failed tests ]-----' |
                    |                                               |                         |
                    |   output: code pushed to fork/branch          |                         |
                    +----------------------+------------------------+                         |
                                           |   *: these may happen before commits             |
                                           |      but should also happen before pushing       |
                                           |      code or opening a PR                        |
                                ==== Local/PR line ====                                       |
                                           |                                                  |
                                           |                                                  |
                    +-----------------------------------------------+                         |
                    |   input: code from fork/branch                |                         |
                    |                                               |                         |
                    |       Unit test suite/code review             +--[ failed tests or   ] /|
                    |                                               |  [ changes requested ]' |
                    |   output: code merged to main                 |                         |
                    +----------------------+------------------------+                         |
                                           |                                                  |
                                           |                                                  |
                                           V                                                  |
                     +-----------------------------------------------+                        |
                     |   input: latest code on main                  |                        |
                     |                                               |                       ,'
                     |       build docs + .whl                       |                      /
                     |       Full suite of unit+integration tests    +--[ Failed tests ]---'
                     |                                               |
                     |   output: release artifacts (build + docs)    |
                     +----------------------+------------------------+
                                            |
                                            |
                                            V
                      +---------------------------------------------------+
                      |   input: release artifacts                        |
                      |                                                   |
                      |       Copy release artifacts to archive/nightly   |
                      |       (keep last 30 builds, min 30 days)          |
                      |                                                   |
                      |   output: release artifacts (build + docs)        |
                      +----------------------+----------------------------+
                                             |
                                             |
                                             V
                      +---------------------------------------------------+
                      |   input: tagged release artifacts                 |
                      |                                                   |
                      |       Push release to PyPI/Docs to ????           |
                      |                                                   |
                      |   output: release on PyPI                         |
                      +---------------------------------------------------+



Details
-------

Local Pre-Commit Hooks, Tests, and Docs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running pre-commit hooks locally will help ensure before a PR is submitted that
it looks reasonable at first glance. There may be more underlying issues, but
the pre-commit hooks will catch things like formatting issues, lint issues,
completely missing docs, etc.

Running the tests and building/viewing the documentation locally is the next
step - this is the last step for contributors to check that their code,
documentation, and tests are organized and ready to open a PR. This step is an
essential part of the pipeline, since updates require test coverage and
documentation.

**On Murphy**: failures here simply require re-running the process, as this is
simply a local process. The pre-commit hooks should be fail safe, not touching
anything if they can't do it safely, or just printing error messages.

Unit Tests (and More) On Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every pull request will run the pre-commit hook checks, build the docs, build
and do a local install of the package, and run the unit test suite. We may want
to enable certain integration tests to run on pull requests, or define a
manual(ish) process to run the integration tests on PRs, but at minimum the PR
will run:

* pre-commit hooks
* docs build
* unit test suite

Any failure here MUST be addressed before the PR may be merged. The entire unit
test suite must be green before the PR is merged. Merging also requires that
the full main branch tests are green. Otherwise, PRs should not be merged
(unless of course they're fixing the full test suite).

**On Murphy**: We may run out of time on our runners, or they may otherwise
crash and burn. Whatever runners we're using should be able to be restarted and
re-run the PR checks. The input here is a particular revision, and the output
will be code merged to the `main` branch.

Integration (Post-Merge) Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because the unit test suite is very narrow - isolating against many of the
extension module dependencies - we want more broad, comprehensive tests. While
the unit tests will *trust* that things work as expected, the integration tests
will *verify* that things work as expected. *Correctly running integration tests
will give us confidence that the assumptions made in the unit test suite are
safe assumptions.*

Integration tests should not only run against the current/latest merge to main
with the specified dependencies, but they should also run against the newest
versions of as many dependencies as possible. Running against several different
versions of Salt (including the latest code in git) and other dependencies will
ensure that as APIs change that we learn of it sooner rather than later, and
can anticipate breaking changes rather than react to them.

Like unit test section of the pipeline, the integration test (which should also
run the unit tests) should build the module and install it. The tests should be
ran against the installed package version. This process will help detect
potential packaging issues earlier rather than later.


Failures in the integration test run are considered an **EMERGENCY**. No code
should be merged, besides fixes for the tests, until the integration tests are
running successfully again. It would be a good idea for integration test
failures to automatically create an issue in GitHub, or re-open an existing
issue that corresponds to the same test, to help identify flaky integration
tests. Integration test failures should also have a corresponding unit test
that produces the same behavior by mocking out the conditions that caused the
integration test failure -- this will ensure that regressions aren't
re-introduced, as well as allow failure detection in the fast-running unit test
suite.

On a successful pass through the integration tests, the result will be a
``.whl`` package of the library, as well as the documentation. These artifacts
should be kept for the last 30 days and the last 30 builds, minimum. In other
words, if we built 2x per day for 30 days we would keep the last 60 builds.
Alternatively, if we built ever other day for 60 days, we would keep the last
30 days, even though 15 of them would be more than 30 days old.

These old artifacts will be useful if we need to go back and detect issues in
our build process, or other uncommon problems. 30 days/30 builds is an
arbitrary number - we could store more artifacts if it doesn't make much of an
impact.

All of these artifacts should be made public - perhaps via PyPI or GitHub. PyPI
would be easy, but we would be increasing the load on PyPI - if we did that we
should investigate helping to fund PyPI.

Because these tests run against private cloud infrastructure, they must be
designed to take advantage of config files that can be provided either at a
relative location or a configurable location in the filesystem. That allows the
CI pipeline the ability to provide connection secrets in a way that is unlikely
to leak in any test logging.

**On Murphy:** Integration tests, being closer to real-world use, can fail for
any number of reasons. There can be some breakage with the network. DNS issues.
The underlying system configuration could fail. GitHub could fall over. We
should work to anticipate these problems and avoid them ahead of time, but if
we are unable to, we should address them as they arise. Since the input of this
step is the code at the main branch, this step should not be considered
successful until the release artifacts for that particular commit on ``main``
have been uploaded to the correct location.

Tagging and Release
^^^^^^^^^^^^^^^^^^^

Assuming that all tests continue to stay green, a Release Candidate (RC) will
be released. These will always be deployed to PyPI - the version specifier will
ensure that pip installs only upgrade to the RC when the ``--pre`` flag is
passed, but will make it trivial for interested users to test the latest
version.

Because the only difference between a regular build and a RC/final release
build is tagging and potentially documentation, the release will follow the
same process as any other build. Our confidence should be high that our test
suite and full pipeline will succeed, with such trivial non-code changes.

The only difference between the regular "nightly build" process, and a PyPI
releas, will be that if there is a tag corresponding to the commit that created
this build, in addition to uploading the artifacts to our archive, the
artifacts will also be released to PyPI and whatever location is hosting our
docs.

**On Murphy**: something could happen here, failing to upload the release
artifacts to PyPI/doc hosting. In the *absolute* worst case, the machine
holding our release artifacts would be hit by a meteor at the same time the
datacenter holding our archive falls into a sinkhole. In that case, we would
have to re-start the entire build process. But what is more likely is that the
upload would simply fail, and we would have to continue to re-try uploading the
artifacts, either from the build machine or a copy from our archive.

Notifications
^^^^^^^^^^^^^

The final step of the release will be notifying the Salt community of the
release. As of this writing there is no automation to generate notices via IRC,
Slack, email, and social media, but since the Salt Project will have a number
of extension modules it seems reasonable that we would want to build this type
of automation.

Consequences
------------

The optimistic result is that deploying new releases will be as simple as
pushing a new tag to the repository.

There will be consequences in terms of build times - both blocking PRs as well
as post merge for the full test runs. Also, this infrastructure is code, and
code must be maintained, so there will be a maintenance cost to the
infrastructure.

But ultimately, this should result in reliable deployments with feedback coming
as early in the cycle as possible.
