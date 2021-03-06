from logging import getLogger, LoggerAdapter

import click


class RSLogger(LoggerAdapter):
    def __init__(self):
        super(RSLogger, self).__init__(getLogger('rsconnect'), {})
        self._in_feedback = False
        self._have_feedback_output = False

    def set_in_feedback(self, value):
        self._in_feedback = value
        self._have_feedback_output = False

    def process(self, msg, kwargs):
        msg, kwargs = super(RSLogger, self).process(msg, kwargs)
        if self._in_feedback:
            if not self._have_feedback_output:
                print()
                self._have_feedback_output = True
            msg = click.style(' %s' % msg, fg='green')
        return msg, kwargs

    def setLevel(self, level):
        """
        Set the specified level on the underlying logger.

        **Note:** This is present in newer Python versions but since it's missing
        from 2.7, we replicate it here.
        """
        self.logger.setLevel(level)


logger = RSLogger()
