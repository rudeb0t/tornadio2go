from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunServerCommand
from django.utils import autoreload
from optparse import make_option

import django.core.handlers.wsgi
import os
import socket
import sys
import tornadio2
import tornadio2.router
import tornado
import tornado.httpserver
import tornado.web
import tornado.wsgi

from tornadio2go.models import TornadioClient
from tornadio2go.signals import pre_add_handlers, post_add_handlers, \
    pre_server_start, post_server_start, pre_ioloop_start

class Command(RunServerCommand):
    option_list = BaseCommand.option_list + (
        make_option('--ipv6', '-6', action='store_true', dest='use_ipv6', default=False,
            help='Tells Tornado to use a IPv6 address.'),
        make_option('--noreload', action='store_false', dest='use_reloader', default=True,
            help='Tells TornadIO2Go to NOT use the auto-reloader.'),
        make_option('--num-process', action='store', type='int', dest='num_process', default=1,
            help='Number of Tornado worker processes. Disables auto-reloader if not set to 1.'),
    )

    help = "Starts a Tornado Web server."
    args = '[optional port number, or ipaddr:port]'

    def run(self, *args, **options):
        """
        Runs the server, using the autoreloader if needed
        """
        use_reloader = options.get('use_reloader')
        num_process = int(options.get('num_process'))

        # Only enable auto-reloader if we are running in single-process mode
        # (the default). Otherwise, we disable it because it only leads to all
        # sorts of problems.
        if use_reloader and num_process == 1:
            autoreload.main(self.inner_run, args, options)
        else:
            self.inner_run(*args, **options)

    def inner_run(self, *args, **options):
        from django.conf import settings
        from django.utils import translation
        import logging

        use_reloader = options.get('use_reloader')
        num_process = int(options.get('num_process'))
        verbosity = int(options.get('verbosity'))
        if verbosity == 1:
            logging_level = logging.ERROR
        elif verbosity == 2:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.WARNING

        logging.getLogger().setLevel(logging_level)

        shutdown_message = options.get('shutdown_message', '')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        tornadio2go_settings = getattr(settings, 'TORNADIO2GO', dict())
        tornadio2_connection_class = tornadio2go_settings.get('SOCKETCONNECTION_CLASS', None)
        tornadio2_user_settings = tornadio2go_settings.get('USER_SETTINGS', dict())
        tornado_options = tornadio2go_settings.get('TORNADO_OPTIONS', dict())
        tornado_handlers = list(tornadio2go_settings.get('TORNADO_HANDLERS', []))

        TornadioConnection = None
        if tornadio2_connection_class:
            _classname = tornadio2_connection_class.split('.')[-1]
            _package = '.'.join(tornadio2_connection_class.split('.')[:-1])
            _module = __import__(_package, fromlist=[_classname+'xx'])
            TornadioConnection = getattr(_module, _classname)

        if num_process == 0:
            tornado_process = 'auto'
        elif num_process == 1:
            tornado_process = 'single-process'
        else:
            tornado_process = '%d processes' % num_process

        self.stdout.write("Validating models...\n\n")
        self.validate(display_num_errors=True)
        self.stdout.write((
            "%(started_at)s\n"
            "Django version %(version)s, using settings %(settings)r\n"
            "Tornado version %(tornado_version)s server is running at http://%(addr)s:%(port)s/ (%(tornado_process)s)\n"
            "TornadIO2 version %(tornadio2_version)s: %(tornadio2_status)s\n"
            "Auto-reloader is %(reloader)s.\n"
            "Quit the server with %(quit_command)s.\n"
        ) % {
            "started_at": datetime.now().strftime('%B %d, %Y - %X'),
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "addr": self._raw_ipv6 and '[%s]' % self.addr or self.addr,
            "port": self.port,
            "quit_command": quit_command,
            "tornado_version": tornado.version,
            "tornado_process": tornado_process,
            "tornadio2_version": '.'.join(map(lambda x: str(x), tornadio2.__version__)),
            "tornadio2_status": (TornadioConnection and 'enabled' or 'disabled'),
            "reloader": ((use_reloader and num_process == 1) and 'enabled' or 'disabled'),
        })
        # django.core.management.base forces the locale to en-us. We should
        # set it up correctly for the first request (particularly important
        # in the "--noreload" case).
        translation.activate(settings.LANGUAGE_CODE)

        try:
            tornado_app = tornado.web.Application()
            server = tornado.httpserver.HTTPServer(tornado_app, **tornado_options)
            server.bind(
                port = self.port,
                address = self.addr,
                family = self.use_ipv6 and socket.AF_INET6 or socket.AF_INET
            )
            pre_server_start.send(sender=server, tornado_app=tornado_app)
            server.start(num_process)
            post_server_start.send(sender=server, tornado_app=tornado_app)

            # TornadioRouter constructor calls IOLoop.instance() which causes
            # HTTPServer.start(num_process) to fail if num_process is not 1. So
            # we set up our app and handlers here.
            wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
            handlers = tornado_handlers + [
                ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app))
            ]
            if TornadioConnection:
                TornadioClient.objects.all().delete()
                tornadio2_router = tornadio2.router.TornadioRouter(TornadioConnection, tornadio2_user_settings)
                handlers = tornadio2_router.urls + handlers

            pre_add_handlers.send(sender=server, tornado_app=tornado_app)
            tornado_app.add_handlers('.*$', handlers)
            post_add_handlers.send(sender=server, tornado_app=tornado_app)

            pre_ioloop_start.send(sender=server, tornado_app=tornado_app)
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
