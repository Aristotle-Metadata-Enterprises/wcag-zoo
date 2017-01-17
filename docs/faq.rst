Frequently Asked Questions
==========================

Can I use this to check my sites accessibility at different breakpoints?
------------------------------------------------------------------------

Yes! Making sure your site is accessible at different screen sizes is important so
this is vitally important. By default, WCAG-Zoo validators ignore ``@media`` rules, but
if you are using CSS ``@media`` rules to provide different CSS rules to different users,
you can declare which media rules to check against when running commands.

These can be added using the ``--media_rules`` command line flag (``-M``) or using the
``media_rules`` argument in Python. Any CSS ``@media`` rule that matches against *any* of
the listed ``media_rules`` to check will be used, *even if they conflict*.

For example, below are some of the media rules used in the 
`Twitter Bootstrap CSS framework <http://getbootstrap.com/>`_ ::

    1. @media (max-device-width: 480px) and (orientation: landscape) {
    2. @media (max-width: 767px) {
    3. @media screen and (max-width: 767px) {
    4. @media (min-width: 768px) {
    5. @media (min-width: 768px) and (max-width: 991px) {
    6. @media screen and (min-width: 768px) {
    7. @media (min-width: 992px) {
    8. @media (min-width: 992px) and (max-width: 1199px) {
    9. @media (min-width: 1200px) {

The following command will check rules 4, 5 and 6 as all contain the string ``(min-width: 768px)``::

   zookeeper molerat --media_rules="(min-width: 768px)"

Note that this command will check media rules where the maximum width is 767px
and the minimum width is 768px::

  zookeeper molerat -M="(min-width: 768px)" -M="(max-width: 767px)"
  
In reality a browser would never render these as the rules conflict, but zookeeper isn't that smart yet.


Why is it important to check the accesibility of hidden elements?
-----------------------------------------------------------------

Elements such as these often have their visibility toggled using Javascript in a browser, as such testing hidden elements ensures that
if they become visible after rendering in the browser they conform to accessibility guidelines.
 
By default, all WCAG commands check that hidden elements are valid, however they also accept a ``ignore_hidden`` argument 
(or ``-H`` on the command line) that prevents validation of elements that are hidden in CSS, 
such as those contained in elements that have a ``display:none`` or ``visibility:hidden`` directive.

Why does my page fail a contrast check when the contrast between foreground text color and a background image is really high?
-----------------------------------------------------------------------------------------------------------------------------

Molerat can't see images and determines text contrast by checking the contrast between the calculated CSS rules for the
foreground color (``color``) and background color (``background-color``) of a HTML element. If the element hasn't got a 

Consider white text in a div with a black background *image* but no background color, inside a div with a white back ground, like that
demonstrated below ::

    +--------------------------------------------------+
    |  (1) Black text / White background               |
    |                                                  |
    |  +-----------------------------------------+     |
    |  | <div class='inner' id='hero_text'>      |     |
    |  | (2) White text / Transparent background |     |
    |  |                  Black bckrgound image  |     |
    |  |                                         |     |
    |  +-----------------------------------------+     |
    +--------------------------------------------------+

In the above example, until the image loads the text in div (2) is invisible.
If the connection is interrupted or a user has images disabled, the text would be unreadable.
**The ideal way to resolve this is to add a background color to the inner ``div`` to ensure all users can read it.**
If this isn't possible, to resolve this error, add the class or id to the appropriate exclusion rule. For example, from the command line::

    zookeeper molerat somefile.html --skip_these_classes=inner
    zookeeper molerat somefile.html --skip_these_ids=hero_text

Or when calling as a module::

    Molerat(..., skip_these_classes=['inner'])
    Molerat(..., skip_these_ids=['hero_text'])
