===========
TornadIO2Go
===========

TornadIO2Go integrates `TornadIO2`_ with your Django project. It allows you to
run both your Django project and TornadIO2 app from within the same `Tornado`_
server. Or you can just use it as a production-ready ``runserver`` substitute.

Installation
============

The quickest way to install is via `pip`_ from within a `virtualenv`_.::

    pip install https://github.com/rudeb0t/tornadio2go/archive/master.zip#egg=TornadIO2Go

Alternatively, you can opt to use an "editable" installation::

    pip install -e https://github.com/rudeb0t/tornadio2go.git#egg=TornadIO2Go

Quick Start
===========

Add ``tornadio2go`` to your ``INSTALLED_APPS`` and then run ``syncdb``. This
will install the models used by TornadIO2Go. Create your
``tornadio2.SocketConnection`` subclass and write your event handlers as
usual. Then add the following to your ``settings.py``::

    TORNADIO2GO = {
        'SOCKETCONNECTION_CLASS': 'path.to.socketConnectionClass'
    }

Then from the command line, start the TornadIO2 server::

    python manage.py runtornadio2

This will start the server bound to 127.0.0.1 and listening on port 8000.

Django Settings
===============

All of TornadIO2Go's settings are found in the Django setting ``TORNADIO2GO``.
This is a simple Python ``dict``. Available settings, all of them are optional:

* ``SOCKETCONNECTION_CLASS`` - this should be the complete path to the
  ``tornadio2.SocketConnection`` subclass. If this is not specified,
  ``runtornadio2`` will run your Django project in a Tornado web server.

* ``USER_SETTINGS`` - this is a ``dict`` containing options that should be
  when creating a new ``tornadio2.router.TornadioRouter`` instance. This is
  only used if you specify ``SOCKETCONNECTION_CLASS``.

* ``TORNADO_OPTIONS`` - this is a ``dict`` of all the options that you wish to
  use for the ``tornado.httpserver.HTTPServer`` instance that will be created.
  See `HTTPServer`_ documentation.

* ``TORNADO_HANDLERS`` - this is a list of handlers that you want to be added
  before the `FallbackHandler`.
  
Command Line Options
====================

The ``runtornadio2`` command has similar command line options to Django's
``runserver`` command. Do:::

    python manage.py runtornadio2 --help

To display a list of available options. Typical usage is:::

    python manage.py runtornadio2 [options] [optional port number, or ipaddr:port]

To run a multi-process server, use the ``--num-process`` option and set it to
either zero or any number greater than one. Set to zero to automatically
detect the number of available CPU cores and fork the appropriate number of
processes. Set to any number greater than one to fork a specific number of
processes.

Running With supervisord
========================

In order to run tornadio2go under `supervisord`_ you must use the `--noreload`
or `--num-process=1` flag in the command parameter for the ini section of your
configuration file.  `supervisord` does not like it when its supervised
programs do a `fork()` and the reloader does just that.

Signals
=======

*Experimental in 1.0.3*

Version 1.0.3 introduces signals which are sent during different stages of
initialization. The list of signals (in the order that they are sent) are as
follows:

* `pre_server_start`

* `post_server_start`

* `pre_add_handlers`

* `post_add_handlers`

The signals handlers will all receive the `tornado.web.Application` object in
the `tornado_app` keyword argument. Unless otherwise indicated, the `sender` is
always the `tornado.httpserver.HTTPServer` object.

This feature is currently marked as **EXPERIMENTAL** and might change in future
versions.

.. _TornadIO2: https://github.com/MrJoes/tornadio2
.. _Tornado: http://www.tornadoweb.org/
.. _pip: http://pypi.python.org/pypi/pip
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _HTTPServer: http://www.tornadoweb.org/documentation/httpserver.html#http-server
.. _supervisord: http://supervisord.org/
