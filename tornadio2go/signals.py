from django.dispatch import Signal


pre_server_start = Signal(providing_args=['tornado_app'])
post_server_start = Signal(providing_args=['tornado_app'])
pre_add_handlers = Signal(providing_args=['tornado_app'])
post_add_handlers = Signal(providing_args=['tornado_app'])
pre_ioloop_start = Signal(providing_args=['tornado_app'])
