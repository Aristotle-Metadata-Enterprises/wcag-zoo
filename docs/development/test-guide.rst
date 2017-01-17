Guide to writing tests for commands
===================================

To make writing tests easier, tests can be declaratively written in HTML using ``data-*`` attributes to specify
the command to check a HTML document against, and the expected errors.

The available attributes are:

* ``data-wcag-test-command`` (only on the root ``html`` element) - the specific zookeeper
    validator to use for the HTML file.
* ``data-wcag-arg-\*`` (only on the root ``html`` element) - attributes starting with
    ``data-wcag-arg-`` specify arguments to pass when running the given command.
    Each attribute constitutes a key/value pair, with the key
    corresponding to everything captured by the asterisk (``*``) above.
    All values are evaluated in Python and are expected to be valid Python
    literals - as such numbers are treated as numbers, booleans are booleans, and strings need to be
    double quoted.
* ``data-wcag-failure-code`` and ``data-wcag-warning-code`` - can be located on any element in the body.
    These specify both that a given node should produce a failure or warning when using the above command
    and arguments, as well as the expected error code.

Below is an example that tests the ``molerat`` command, for WCAG 2.0-AA compliance
and checks using a specific media rule to check a page for use on small screens.

.. literalinclude:: ../../tests/html/molerat-color-contrast-mobile-hate.html
   :language: html

This is equivilent to running the following at the command line::

  zookeeper molerat the_file_above.html \
    --level=AA \
    --media_rules='max-width: 600px' \
    --skip_these_classes=sneaky

or the following python command::

    from wcag_zoo.validators.molerat import Molerat
    
    validator = Molerat(
        level="AA",
        media_rules=['max-width: 600px'],
        skip_these_classes=["sneaky"]
        ).validate_document(the_text_above)
