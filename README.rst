==============
Python libnacl
==============

This library is used to gain direct access to the functions exposed by
Daniel J. Bernstein's nacl library via libsodium. It has
been constructed to maintain extensive documentation on how to use nacl
as well as being completely portable. The file in libnacl/__init__.py
can be pulled out and placed directly in any project to give a single file
binding to all of nacl.

Fork by @Tho85
==============

This is a fork of the original code at https://github.com/saltstack/libnacl.
Its purpose is to install a vendored version of libsodium, so that this
library can be used in environments where libsodium is not installed by
default.

For more background, please see this issue: https://github.com/jheling/freeathome/issues/130


Higher Level Classes
====================

The libnacl code also ships with many high level classes which make nacl
cryptography easy and safe, for documentation please see:
http://libnacl.readthedocs.org/

Why libnacl
===========

There are a number of libraries out there binding to libsodium, so why make
libnacl?

1. libnacl does not have any non-python hard deps outside of libsodium
2. libnacl does not need to be compiled
3. libnacl is easy to package and very portable
4. Inclusion of high level pythonic encryption classes
5. Ability to have a single embeddable and transferable bindings file
   that can be added directly to python applications without needing
   to dep libnacl

This makes libnacl very portable, very easy to use and easy to distribute.

Install
=======

The libnacl code is easiy installed via a setup.py from the source or via pip.

From Source:

.. code-block:: bash

    tar xvf libnacl-1.5.2.tar.gz
    cd libnacl-1.5.2
    python setup.py install

Via Pip:

.. code-block:: bash

    pip install libnacl

Remember that libnacl can be installed for python 2 and 3.

Linux distributions
-------------------

Libnacl is shiped with many linux distributions, check your distribution
package manager for the package ``python-libnacl``, ``python2-libnacl``
and/or ``python3-libnacl``.
