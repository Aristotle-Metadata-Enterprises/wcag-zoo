WCAG Zoo - Scripts for automated accessiblity validation
========================================================

|wcag-zoo-aa-badge| |appveyor| |travis| |coverage| |pypi| |docs|

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/uyo3jx1em3cmjrku?svg=true
   :target: https://ci.appveyor.com/project/LegoStormtroopr/wcag-zoo
   :alt: Appveyor testing status
   
.. |travis| image:: https://travis-ci.org/data61/wcag-zoo.svg?branch=master
    :target: https://travis-ci.org/data61/wcag-zoo
    :alt: Travis-CI  testing status

.. |coverage| image:: https://coveralls.io/repos/github/data61/wcag-zoo/badge.svg
    :target: https://coveralls.io/github/data61/wcag-zoo
    :alt: Coveralls code coverage

.. |pypi| image:: https://badge.fury.io/py/wcag-zoo.svg
    :target: https://badge.fury.io/py/wcag-zoo
    :alt: Current version on PyPI

.. |docs| image:: https://readthedocs.org/projects/wcag-zoo/badge/?version=latest
    :target: http://wcag-zoo.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. rtd-inclusion-marker

What is it?
-----------

WCAG-Zoo is a set of command line tools that help provide basic validation of HTML
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

Plus, integrating accessibility into your build scripts shows that you really care about the usability of your site.
These tools won't pick up every issue around accessibility, but they'll pick up enough (and do so automatically)
and helps demonstrate a commitment to accessibility where possible.

That sounds like a lot of work, is it really that useful?
---------------------------------------------------------

Granted, accessibility is tough - and you might question how useful it is.
If you have an app targeted to a very niche demographic and are working on tight timeframes,
maybe accessibility isn't important right now.

But some industries, such as Government, Healthcare, Legal and Retail all care **a lot** about WCAG compliance.
To the point that in some areas it is legislated or mandated.
In some cases not complying with certain accessibility guidelines `can even get sued <https://www.w3.org/WAI/bcase/target-case-study>`_
can lead to large, expensive lawsuits!

If you care about working in any of the above sectors, being able to *prove* you are compliant can be a big plus,
and having that proof built in to your testing suite means identiying issues earlier before they are a problem.

But all my pages are dynamically created and I use a CSS pre-processor
----------------------------------------------------------------------

Doesn't matter. If you can generate them, you can output your HTML and CSS in a build script
and feed them into the WCAG-Zoo via the command line.


But I have lots of user-generated content! How can I possibly test that?
------------------------------------------------------------------------

It doesn't matter if your site is mostly user-generated pages. Testing what you can sets a good example
to your users. Plus many front-end WYSIWYG editors have their own compliance checkers too.
This also sets a good example to your end-users as they know that the rest of the site is WCAG-Compliant
so they should probably endevour to make sure their own content is too.

Since this is a Python library if you are building a dynamic site where end users can edit HTML that
uses Python on the server side you can import any of the validators directly into your code
so you can confirm that the user created markup is valid as well.

Lastly, if you are building a dynamic site in a language other than Python you can run any of the command
line scripts with the ``--json`` or ``-J`` flag and this will produce a JSON output that can be parsed and
used in your preferred target language.

For details on this see the section in the documentation titled "`Using WCAG-Zoo in languages other than Python <//wcag-zoo.readthedocs.io/en/latest/development/using_wcag_zoo_not_in_python.html>`_".

Do I have to check *every* page?
--------------------------------

The good news is probably not. If your CSS is reused across across lots of your site
then checking a handful of generate pages is probably good enough.

You convinced me, how do I use it?
----------------------------------

Two ways:

1. `In your build and tests scripts, generate some HTML files and use the command line tools so that
   you can verify your that the CSS and HTML you output can be read. <//wcag-zoo.readthedocs.io/en/latest/development/using_wcag_zoo_not_in_python.html>`_

2. `If you are using Python, once installed from pip, you can import any or all of the tools and
   inspect the messages and errors directly using <//wcag-zoo.readthedocs.io/en/latest/development/using_wcag_zoo_in_python.html>`_::

       from wcag_zoo.molerat import molerat
       messages = molerat(html=some_text, ... )
       assert len(messages['failed']) == 0


I've done all that can I have a badge?
--------------------------------------

Of course! You are on the honour system with these for now. So if you use WCAG-Zoo in your tests
and like Github-like badges, pick one of these:

* |wcag-zoo-aa-badge| ``https://img.shields.io/badge/WCAG_Zoo-AA-green.svg``
* |wcag-zoo-aaa-badge| ``https://img.shields.io/badge/WCAG_Zoo-AAA-green.svg``

.. |wcag-zoo-aa-badge| image:: https://img.shields.io/badge/WCAG_Zoo-AA-green.svg
   :target: https://github.com/data61/wcag-zoo/wiki/Compliance-Statement
   :alt: Example badge for WCAG-Zoo Double-A compliance
   
.. |wcag-zoo-aaa-badge| image:: https://img.shields.io/badge/WCAG_Zoo-AAA-green.svg
   :target: https://github.com/data61/wcag-zoo/wiki/Compliance-Statement
   :alt: Example badge for WCAG-Zoo Triple-A compliance

ReSTructured Text::

    .. image:: https://img.shields.io/badge/WCAG_Zoo-AA-green.svg
       :target: https://github.com/data61/wcag-zoo/wiki/Compliance-Statement
       :alt: This repository is WCAG-Zoo compliant

Markdown::

    ![This repository is WCAG-Zoo compliant][wcag-zoo-logo]
    
    [wcag-zoo-logo]: https://img.shields.io/badge/WCAG_Zoo-AA-green.svg "WCAG-Zoo Compliant"

Installing
----------

* Stable: ``pip3 install wcag-zoo``
* Development: ``pip3 install https://github.com/LegoStormtroopr/wcag-zoo``


How to Use
----------

All WCAG-Zoo commands are exposed through ``zookeeper`` from the command line.

Current critters include:

* Anteater - checks ``img`` tags for alt tags::

    zookeeper anteater your_file.html --level=AA

* Ayeaye - checks for the presence and uniqueness of accesskeys::

    zookeeper ayeaye your_file.html --level=AA

* Molerat - color contrast checking::

    zookeeper molerat your_file.html --level=AA

* Parade - runs all validators against the given files with allowable exclusions::

    zookeeper parade your_file.html --level=AA
   
* Tarsier - tree traveral to check headings are correct::

    zookeeper tarsier your_file.html --level=AA

For more help on zookeeper from the command line run::

    zookeeper --help

Or for help on a specific command::

    zookeeper ayeaye --help

Limitations
-----------

At this point, WCAG-Zoo commands **do not** handle nested media queries, but they do support
single level media queries. So this will be interpreted::

    @media (min-width: 600px) and (max-width: 800px) {
        .this_rule_works {color:red}
    }

But this won't (plus this isn't supported across some browsers)::

    @media (min-width: 600px) {
        @media (max-width: 800px) {
            .this_rule_wont_work {color:red}
        }
    }
