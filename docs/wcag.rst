WCAG guideline index and validator reference
============================================

This is an index of Web Accessibility Content Guidelines that can be verified using WCAG-Zoo
as well as the techniques used for verification and the validators which perform the validation.

- `1.1.1 - Nontext Content <https://www.w3.org/TR/UNDERSTANDING-WCAG20/text-equiv-all.html>`_

  * `H37: Using alt attributes on img elements 
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/H39>`_ - ``anteater``

- `1.3.1 - Info and Relationships <https://www.w3.org/TR/UNDERSTANDING-WCAG20/content-structure-separation-programmatic.html>`_

  * `H42: Using h1-h6 to identify headings
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/H42>`_ - ``tarsier``

- `1.4.3 - Contrast (Minimum) <https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html>`_

  * `G18: Ensuring that a contrast ratio of at least 4.5:1 exists between text (and images of text) and background behind the text
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G18>`_  - ``molerat``
  * `G145: Ensuring that a contrast ratio of at least 3:1 exists between text (and images of text) and background behind the text
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G145>`_  - ``molerat`` (large text only)

- `1.4.6 - Contrast (Enhanced) <https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast7.html>`_

  * `G17: Ensuring that a contrast ratio of at least 7:1 exists between text (and images of text) and background behind the text
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G17>`_ - ``molerat`` (using AAA compliance)
  * `G18: Ensuring that a contrast ratio of at least 4.5:1 exists between text (and images of text) and background behind the text
    <http://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G18>`_  - ``molerat``  (large text only, using AAA compliance)

- `2.1.1 - Keyboard <https://www.w3.org/TR/UNDERSTANDING-WCAG20/keyboard-operation-keyboard-operable.html>`_

  * `G90: Providing keyboard-triggered event handlers
    <https://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G90>`_ - ``ayeaye`` (check for clashes with accesskeys).


Future additions
----------------

The following guidelines and techniques have been identified as potential
additions to the WCAG-Zoo.

- 1.1.1 - Nontext Content

  * H53, H44
  * H36 - Make sure input tags with src have alt or text
  * H30 - Make sure links have text

- 1.2.3 - Audio Description or Media Alternative (Prerecorded)  - H96
- 1.3.1 - Info and Relationships
- 2.4.1 - Bypass blocks - H69
- 2.4.2 - Page titled - H25 + G88 (very basic)
- 2.4.7 - Focus Visible - ( for :focus)
- 3.1.1 - Language of Page - H57
- 4.1.1 - Parsing H74, H75
