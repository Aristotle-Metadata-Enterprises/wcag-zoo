Frequently Asked Questions
==========================

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
