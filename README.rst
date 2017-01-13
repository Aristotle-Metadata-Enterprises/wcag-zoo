WCAG Zoo - Scripts for automated accessiblity validation
========================================================

.. rtd-inclusion-marker

What is it?
-----------

WCAG-Zoo is a set of POSIX-like command line tools that help provide basic validation of HTML
against the accessibility guidelines laid out by the W3C Web Content Accessibility Guidelines 2.0.

Each tool checks against a limited set of these and is designed to return simple text output and returns an 
error (or success) code so it can be integrated into continuous build tools like Travis-CI or Jenkins.
It can even be imported into your Python code for additional functionality.

Why should I care about accessibility guidelines?
-------------------------------------------------

Accessibility means that everyone can use your site. We often forget that not everyone
has perfect vision - or even has vision at all! Complete or partial blindess, color-blindness or just old-age
can all impact how readily accessible your website can be. 

By building accessibility checking into your build scripts you can be relatively certain that all people can
readily use your website. And if you come across an issue, you identify it early - before you hit production
and they start causing problems for people.

Plus, integrating accessibility into your build scripts shows that you really care about the usability of your site. These tools won't pick up every issue around accessibility, but they'll pick up enough (and do so automatically) and its about demonstrating a commitment to accessibility wherever you can.

That sounds like a lot of work, is it really that useful?
---------------------------------------------------------

Granted, accessibility is tough - and you might question how useful it is. If you have an app targeted to a very niche demographic and are working on tight timeframes, maybe accessibility isn't important right now.

But some industries, like Government, Healthcare, Legal and Retail all care about WCAG compliance -
**a lot**! To the point that in some places its legislated. In some cases not complying with certain accessibility guidelines `can even get sued <https://www.w3.org/WAI/bcase/target-case-study>`_!

If you care about working in any of the above sectors, being able to *prove* you are compliant (instead of just claiming it) can be a big plus.

But all my pages are dynamically created and I use a CSS pre-processor
----------------------------------------------------------------------

Doesn't matter. If you can generate them, you can output your HTML them in a build script and feed them in


But I have lots of user-generated content!
------------------------------------------

Doesn't matter. Besides, since this is a Python library, if you are a Python

Do I have to check *every* page?
--------------------------------

The good news is probably not. If your CSS is reused across across lots of your site then checking a handful of generate pages is probably good enough.

You convinced me, how do I use it?
----------------------------------

Two ways:

1. In your build and tests scripts, generate some HTML files and use the command line tools so
 that you can verify your that the CSS and HTML you output can be read.
 
2. If you are using Python, once installed from pip, you can import any or all of the tools and
 inspect the messages and errors directly using::

   from wcag_zoo.molerat import molerat
   messages = molerat(html=some_text, ... )
   assert len(messages['failed']) == 0

I've done all that can I have a badge?
--------------------------------------

Of course! Pick one of these:

``https://img.shields.io/badge/WCAG_Zoo-AA-green.svg``
``https://img.shields.io/badge/WCAG_Zoo-AAA-green.svg``


Installing
----------

* Stable: ``pip install wcag-zoo``
* Development: ``pip install https://github.com/LegoStormtroopr/wcag-zoo``


How to Use
----------

A bunch of crazy critters that perform automated tests on your HTML to verify
basic compliance with the Web Accessibility Guidelines.

Current critters include:

* Molerat - color contrast checking:

       molerat your_file.html --level=AA
   
   Accepts the 

* Tarsier - tree traveral to check headings are correct::

   tarsier your_file.html --level=AA

* Anteater - checks ``img`` tags for alt tags::

   anteater your_file.html --level=AA


Shared command line arguments:

* ``--level`` [AA or AAA]: Specifies the WCAG2.0 level to use for conformance
   - ``--AA`` short hand for ``--level=AA``
   - ``--AAA`` short hand for ``--level=AAA``

* ``-C, --skip_these_classes`` - Comma-separated list of CSS classes for HTML elements to *not* validate (eg. sr-only)
  Useful if you are using CSS frameworks and want to skip validation for elements with screen reader only classes.

* ``-I, --skip_these_ids`` - Comma-separated list of ids for HTML elements to *not* validate

* ``-v, --verbosity`` : Specifies how much text to print to STDOUT. Possible options:
   - ``0`` - Very little, no errors
   - ``1`` - Print some detail on errors
   - ``2`` - Prints comprehensive information on errors
   - ``3`` - Prints comprehensive information on errors and warnings
