2021-05-19 Building Docs
========================

Status
------

Accepted and Implemented

Context
-------

It is expected that many different contributors with a variety of skill levels
will be contributing to this extension module. Rather than relying on a manual
step to ensure that links get added to the docs folder to the states and
modules, we decided to automate this process.

We did have a manual step using ``nox`` to generate API docs, but that ended
out generating things that were too comprehensive, documenting internal
functionality that wasn't relevant for a user.

Decision
--------

The decision we made was to implement a pre-commit hook within the repository
to automatically create rST files that Sphinx would use to auto-generate the
docs based on the state/module code.


Consequences
------------

By using a pre-commit hook, the only thing that's necessary to have docs
correctly created is to setup pre-commit and run a ``git commit``.

These files *are* (re)-created every time, so there is some extra overhead, but
the number of files in this module should be relatively small, so this
shouldn't be a big problem. It may be necessary later to adjust this approach,
but for now it works well.
