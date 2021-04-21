# Salt Extension Modules for VMware

This is a collection of Salt-maintained extension modules for use with VMware
vSphere, vCenter, ESXi, and friends.

## Security

If you think you've found a security vulnerability, see [Salt's security guide][security].


## Contributing

The [Salt Contributing guide][salt-contributing] has a lot of relevant information,
but if you want to hack on the source, this should get you started:


    # Clone the repo
    git clone --origin salt git@github.com:saltstack/salt-ext-modules-vmware.git

    # Change to the repo dir
    cd salt-ext-modules-vmware

    # Create a new venv
    python3 -m venv env --prompt vmw-ext
    source env/bin/activate

    # Install extension + test dependencies into your environment
    python -m pip install -e .[tests]

    # Run tests!
    python -m nox -e tests-3

    # skip requirements install for next time
    export SKIP_REQUIREMENTS_INSTALL=1


Of course, writing code isn't the only way to contribute! We value
contributions in any of these areas:

- Documentation - especially examples of how to use this module to solve
  specific problems.
- Triaging [issues][issues] and participating in [discussions][discussions]
- Reviewing [Pull Requests][PRs] (we really like [Conventional
  Comments][comments]!)

You could also contribute in other ways:

- Writing blog posts
- Posting on social media about how you used Salt+VMware to solve your
  problems, including videos
- Giving talks at conferences
- Publishing videos
- Asking/answering questions in IRC, Slack, or email groups

Any of these things are super valuable to our community, and we sincerely
appreciate every contribution!


[security]: https://github.com/saltstack/salt/blob/master/SECURITY.md
[salt-contributing]: https://docs.saltproject.io/en/master/topics/development/contributing.html
[issues]: https://github.com/saltstack/salt-ext-modules-vmware/issues
[PRs]: https://github.com/saltstack/salt-ext-modules-vmware/pulls
[discussions]: https://github.com/saltstack/salt-ext-modules-vmware/discussions
[comments]: https://conventionalcomments.org/
