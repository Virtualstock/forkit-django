from django.dispatch import Signal

pre_reset = Signal()
post_reset = Signal()

pre_fork = Signal()
post_fork = Signal()

pre_diff = Signal()
post_diff = Signal()

pre_commit = Signal()
post_commit = Signal()
