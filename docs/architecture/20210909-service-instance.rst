service_instance performance
=================================================

TLDR; service_instance is unlikely to be cached for the foreseeable future.

Background
----------

In order to operate against vCenter, we need to have a connection to it. That
is handled via the ``service_instance``.

All external functions operating against vcenter accept a ``service_instance``.
This is useful for testing. It also allows a user to operate against multiple
service instances at once.

The default value is ``None``, which triggers the creation of a new service
instance.

This is slow.

For performance, a user could reuse a handle to a service instance.

Pushing this on the user is bad.

Solution
--------

How could we handle this for the user?

We have tried decorators to inject the ``service_instance`` if it wasn't
passed explicitly, the salt loader didn't like that (I don't know the
full details). This would slightly simplify the code, but wouldn't directly
help the user; we'd still need a singleton or cache.

Cache
^^^^^

Assuming that the ``service_instance`` manages its connection well and reconnects
when necessary, we could cache it or make it a singleton, something like this:

.. code-block:: python

 def load_service_instance():
     return get_service_instance(opts=__opts__, pillar=__pillar__)

 SI = lazy_object_proxy.Proxy(load_service_instance)

 def foo(service_instance=SI):
     pass

The Salt Loader
^^^^^^^^^^^^^^^

A potential problem is the salt loader and memory leaks. Basically, modules can
be reloaded by salt - the file is read again, then replaces the current module
in ``sys.modules``.

Modules are not designed to be replaced like that and it's easy for this to trigger
memory leaks. We do not fully understand the conditions that cause these leaks.

If we were to do this, we would need to implement the code, then stress test it,
then inspect all of the memory via ``gc.get_objects()`` to ensure that only one
service instance exists. As part of that we'd also need to make sure that only
one service instance *class* exists.

This is because ``type`` and ``isinstance`` don't work as you might expect when
dealing with modules that are reloaded - you end up with multiple class instances
that are identical except for their ``id`` (which is used to calculate class equality).

A Smarter Instance
^^^^^^^^^^^^^^^^^^

If the service instance connection isn't managed well we would need a smarter
object than the mentioned ``lazy_object_proxy``, we would need to auto-reconnect
on certain exceptions.

Hypothetically:

.. code-block:: python

 class ReconnectProxy(lazy_object_proxy.Proxy):
     def __getattr__(self, item):
         try:
             return super().__getattr__(item)
         except ConnectionError:
             self._proxied_obj = load_service_instance(opts=__opts__, pillar=__pillar__)
             return super().__getattr__(item)



Conclusion
----------

This is all doable, but is not a priority.