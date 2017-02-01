Using WCAG-Zoo in other languages
=================================

Below are a small number of example scripts that show how to call the WCAG-Zoo scripts
from a number of target languages to provide runtime support for accessibility checking.

All of the following snippets will either:

* Store a specified string ``my_html`` as the temporary file accessed by the variable ``tmp_file`` or
* Pass a specified string ``my_html`` into the command via stdin

Then:

1. Execute the WCAG command ``wcag_zoo.validators.tarsier`` using Python and store the result as ``results``
2. Capture the ``results`` string and parse it from JSON into the variable ``json_results``
3. Prints the number of failures for the file

All of the following scripts are public domain samples and not guaranteed to work in production in any way.
All scripts should output something similar to ``/tmp/wcag117015-32930-onps7o 1 failures``


Node.JS
-------
File based:

Assuming you have `temp <http://github.com/bruce/node-temp/>`_ installed using ``npm install temp``:

.. literalinclude:: scripts/node_wcag.js
   :language: javascript



Perl
----

File based:

.. literalinclude:: scripts/untested/perl_wcag.pl
   :language: perl


Python
------
Included for reference, but WCAG-Zoo can be `used in Python by importing
validators directly <using_wcag_zoo_in_python.html>`__.

File based:

.. literalinclude:: scripts/python_cli_wcag.py
   :language: python

Ruby
----
Assuming you have installed ``json`` like so: ``gem install json``

File based:

.. literalinclude:: scripts/ruby_wcag.rb
   :language: ruby
