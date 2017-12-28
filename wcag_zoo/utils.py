from __future__ import print_function
from lxml import etree
import click
import os
import sys
from io import BytesIO
import logging
from premailer import Premailer
from premailer.premailer import _cache_parse_css_string

# From Premailer
import cssutils
import re
cssutils.log.setLevel(logging.CRITICAL)
_element_selector_regex = re.compile(r'(^|\s)\w')
FILTER_PSEUDOSELECTORS = [':last-child', ':first-child', ':nth-child', ":focus"]


class Premoler(Premailer):
    def __init__(self, *args, **kwargs):
        self.media_rules = kwargs.pop('media_rules', [])
        super().__init__(*args, **kwargs)

    # We have to override this because an absolute path is from root, not the curent dir.
    def _load_external(self, url):
        """loads an external stylesheet from a remote url or local path
        """
        import codecs
        from premailer.premailer import ExternalNotFoundError, urljoin
        if url.startswith('//'):
            # then we have to rely on the base_url
            if self.base_url and 'https://' in self.base_url:
                url = 'https:' + url
            else:
                url = 'http:' + url

        if url.startswith('http://') or url.startswith('https://'):
            css_body = self._load_external_url(url)
        else:
            stylefile = url
            if not os.path.isabs(stylefile):
                stylefile = os.path.abspath(
                    os.path.join(self.base_path or '', stylefile)
                )
            elif os.path.isabs(stylefile):  # <--- This is the if branch we added
                stylefile = os.path.abspath(
                    os.path.join(self.base_path or '', stylefile[1:])
                )
            if os.path.exists(stylefile):
                with codecs.open(stylefile, encoding='utf-8') as f:
                    css_body = f.read()
            elif self.base_url:
                url = urljoin(self.base_url, url)
                return self._load_external(url)
            else:
                raise ExternalNotFoundError(stylefile)

        return css_body

    def _parse_css_string(self, css_body, validate=True):
        # We override this so we can do our rules altering for media queries
        if self.cache_css_parsing:
            sheet = _cache_parse_css_string(css_body, validate=validate)
        else:
            sheet = cssutils.parseString(css_body, validate=validate)

        _rules = []
        for rule in sheet:
            if rule.type == rule.MEDIA_RULE:
                if any([media in rule.media.mediaText for media in self.media_rules]):
                    for r in rule:
                        _rules.append(r)
            elif rule.type == rule.STYLE_RULE:
                _rules.append(rule)

        return _rules


def print_if(*args, **kwargs):
    check = kwargs.pop('check', False)
    if check and len(args) > 0 and args[0]:
        # Only print if there is something to print
        print(*args, **kwargs)


def nice_console_text(text):
    text = text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    if len(text) > 70:
        text = text[:70] + "..."
    return text


def get_applicable_styles(node):
    """
    Generates a list of dictionaries that contains all the styles that *could* influence the style of an element.

    This is the collection of all styles from an element and all it parent elements.

    Returns a list, with each list item being a dictionary with keys that correspond to CSS styles
    and the values are the corresponding values for each ancestor element.
    """
    styles = []
    for parent in node.xpath('ancestor-or-self::*[@style]'):
        style = parent.get('style', "")

        if not style:
            continue

        styles.append(dict([
            tuple(
                s.strip().split(':', 1)
            )
            for s in style.split(';')
        ])
        )
    return styles


def build_msg(node, **kwargs):
    """
    Assistance method that builds a dictionary error message with appropriate
    references to the node
    """
    error_dict = kwargs
    error_dict.update({
        'xpath': node.getroottree().getpath(node),
        'classes': node.get('class'),
        'id': node.get('id'),
    })
    return error_dict


def get_wcag_class(command):
    from importlib import import_module
    module = import_module("wcag_zoo.validators.%s" % command.lower())
    klass = getattr(module, command.title())
    return klass


class WCAGCommand(object):
    """
    The base class for all WCAG validation commands
    """
    animal = None
    level = 'AA'
    premolar_kwargs = {}

    def __init__(self, *args, **kwargs):
        self.skip_these_classes = kwargs.get('skip_these_classes', [])
        self.skip_these_ids = kwargs.get('skip_these_ids', [])
        self.level = kwargs.get('level', "AA")
        self.kwargs = kwargs

        self.success = {}
        self.failures = {}
        self.warnings = {}
        self.skipped = {}

    def add_success(self, **kwargs):
        self.add_to_dict(self.success, **kwargs)

    def add_to_dict(self, _dict, **kwargs):
        guideline = kwargs['guideline']
        technique = kwargs['technique']
        g = _dict.get(guideline, {})
        g[technique] = g.get(technique, [])
        g[technique].append(build_msg(**kwargs))
        _dict[guideline] = g

    def add_failure(self, **kwargs):
        self.add_to_dict(self.failures, **kwargs)

    def add_warning(self, **kwargs):
        self.add_to_dict(self.warnings, **kwargs)
        # self.warnings.append(build_msg(**kwargs))

    def add_skipped(self, **kwargs):
        self.add_to_dict(self.skipped, **kwargs)
        # self.skipped.append(build_msg(**kwargs))

    def skip_element(self, node):
        """
        Method for adding extra checks to determine if an HTML element should be skipped by the validation loop.

        Override this to add custom skip logic to a wcag command.

        Return true to skip validation of the given node.
        """
        return False

    def check_skip_element(self, node):
        """
        Performs checking to see if an element can be skipped for validation, including check if it has an id or class to skip,
        or if it has a CSS rule to hide it.

        THis class calls ``WCAGCommand.skip_element`` to get any additional skip logic, override ``skip_element`` not this method to
        add custom skip logic.

        Returns True if the node is to be skipped.
        """
        skip_node = False
        skip_message = []
        for cc in node.get('class', "").split(' '):
            if cc in self.skip_these_classes:
                skip_message.append("Skipped [%s] because node matches class [%s]\n    Text was: [%s]" % (self.tree.getpath(node), cc, node.text))
                skip_node = True
        if node.get('id', None) in self.skip_these_ids:
            skip_message.append("Skipped [%s] because node id is [%s]\n    Text was: [%s]" % (self.tree.getpath(node), node.get('id'), node.text))
            skip_node = True
        if self.skip_element(node):
            skip_node = True

        for styles in get_applicable_styles(node):
            # skip hidden elements
            if self.kwargs.get('ignore_hidden', False):
                if "display" in styles.keys() and styles['display'].lower() == 'none':
                    skip_message.append(
                        "Skipped [%s] because display is none is [%s]\n    Text was: [%s]" % (self.tree.getpath(node), node.get('id'), node.text)
                    )
                    skip_node = True
                if "visibility" in styles.keys() and styles['visibility'].lower() == 'hidden':
                    skip_message.append(
                        "Skipped [%s] because visibility is hidden is [%s]\n    Text was: [%s]" % (self.tree.getpath(node), node.get('id'), node.text)
                    )
                    skip_node = True

        if skip_node:
            self.add_skipped(
                node=node,
                message="\n    ".join(skip_message),
                guideline='skipped',
                technique='skipped',
            )
        return skip_node

    def validate_document(self, html):
        """
        Main validation method - validates an entire document, single node from a HTML tree.

        **Note**: This checks the validitity of the whole document
        and executes the validation loop.

        By default, returns a dictionary with the number of successful checks,
        and a list of failures, warnings and skipped elements.
        """
        self.tree = self.get_tree(html)
        self.validate_whole_document(html)
        self.run_validation_loop()

        return {
            "success": self.success,
            "failures": self.failures,
            "warnings": self.warnings,
            "skipped": self.skipped
        }

    def validate_whole_document(self, html):
        """
        Validates an entire document from a HTML element tree.
        Errors and warnings are attached to the instances ``failures`` and ``warnings``
        properties.

        **Note**: This checks the validatity of the whole document, but does not execute the validation loop.

        By default, returns nothing.
        """
        pass

    def validate_element(self, node):
        """
        Validate a single node from a HTML element tree. Errors and warnings are attached to the instances ``failures`` and ``warnings``
        properties.

        By default, returns nothing.
        """
        pass

    def get_tree(self, html):
        if not hasattr(self, '_tree'):
            # Pre-parse
            parser = etree.HTMLParser()
            html = etree.parse(BytesIO(html), parser).getroot()
            kwargs = dict(
                exclude_pseudoclasses=True,
                method="html",
                preserve_internal_links=True,
                base_path=self.kwargs.get("staticpath", "."),
                include_star_selectors=True,
                strip_important=False,
                disable_validation=True,
                media_rules=self.kwargs.get('media_rules', [])
            )
            kwargs.update(self.premolar_kwargs)
            self._tree = Premoler(
                html,
                **kwargs
            ).transform()
        return self._tree

    def run_validation_loop(self, xpath=None, validator=None):
        """
        Runs validation of elements that match an xpath using the given validation method. By default runs `self.validate_element`
        """
        if xpath is None:
            xpath = self.xpath
        for element in self.tree.xpath(xpath):
            if self.check_skip_element(element):
                continue
            if not validator:
                self.validate_element(element)
            else:
                validator(element)

    def validate_file(self, filename):
        """
        Validates a file given as a string filenames

        By returns a dictionary of results from ``validate_document``.
        """
        with open(filename) as file:
            html = file.read()

            results = self.validate_document(html)
            return results

    def validate_files(self, *filenames):
        """
        Validates the files given as a list of strings of filenames

        By default, returns nothing.
        """
        pass

    @classmethod
    def as_cli(cls):
        """
        Exposes the WCAG validator as a click-based command line interface tool.
        """
        @click.command(help=cls.__doc__)
        @click.argument('filenames', required=False, nargs=-1, type=click.File('rb'))
        @click.option('--level', type=click.Choice(['AA', 'AAA', 'A']), default=None, help='WCAG level to test against. Defaults to AA.')
        @click.option('-A', 'short_level', count=True, help='Shortcut for settings WCAG level, repeatable (also -AA, -AAA ')
        @click.option('--staticpath', default='.', help='Directory path to static files.')
        @click.option('--skip_these_classes', '-C', default=[], multiple=True, type=str, help='Repeatable argument of CSS classes for HTML elements to *not* validate')
        @click.option('--skip_these_ids', '-I', default=[], multiple=True, type=str, help='Repeatable argument of ids for HTML elements to *not* validate')
        @click.option('--ignore_hidden', '-H', default=False, is_flag=True, help='Validate elements that are hidden by CSS rules')
        @click.option('--animal', default=False, is_flag=True, help='')
        @click.option('--warnings_as_errors', '-W', default=False, is_flag=True, help='Treat warnings as errors')
        @click.option('--verbosity', '-v', type=int, default=1, help='Specify how much text to output during processing')
        @click.option('--json', '-J', default=False, is_flag=True, help='Prints a json dump of results, with nested guidelines and techniques, instead of human readable results')
        @click.option('--flat_json', '-F', default=False, is_flag=True, help='Prints a json dump of results as a collection of flat lists, instead of human readable results')
        @click.option('--media_rules', "-M", multiple=True, type=str, help='Specify a media rule to enforce')
        def cli(*args, **kwargs):
            total_results = []
            filenames = kwargs.pop('filenames')
            short_level = kwargs.pop('short_level', 'AA')
            kwargs['level'] = kwargs['level'] or 'A' * min(short_level, 3) or 'AA'
            verbosity = kwargs.get('verbosity')
            json_dump = kwargs.get('json')
            flat_json_dump = kwargs.get('flat_json')
            warnings_as_errors = kwargs.pop('warnings_as_errors', False)
            kwargs['skip_these_classes'] = [c.strip() for c in kwargs.get('skip_these_classes') if c]
            kwargs['skip_these_ids'] = [c.strip() for c in kwargs.get('skip_these_ids') if c]
            if kwargs.pop('animal', None):
                print(cls.animal)
                sys.exit(0)
            klass = cls(*args, **kwargs)
            if len(filenames) == 0:
                f = click.get_text_stream('stdin')
                filenames = [f]

            if json_dump:
                import json
                output = []
                for file in filenames:
                    try:
                        html = file.read()
                        results = klass.validate_document(html)
                    except:
                        raise
                        results = {'failures': ["Exception thrown"]}
                    output.append((file.name, results))
                    total_results.append(results)

                print(json.dumps(output))
            elif flat_json_dump:
                import json
                output = []
                for file in filenames:
                    try:
                        html = file.read()
                        results = klass.validate_document(html)
                    except:
                        raise
                        results = {'failures': ["Exception thrown"]}
                    output.append((
                        file.name,
                        {
                            "failures": make_flat(results.get('failures', {})),
                            "warnings": make_flat(results.get('warnings', {})),
                            "skipped": make_flat(results.get('skipped', {})),
                            "success": make_flat(results.get('success', {}))
                        }
                    ))

                print(json.dumps(output))
            else:
                for f in filenames:
                    try:
                        filename = f.name
                        print_if(
                            "Starting - {filename} ... ".format(filename=filename), end="",
                            check=verbosity>0
                        )
                        html = f.read()
                        results = klass.validate_document(html)

                        if verbosity == 1:
                            if len(results['failures']) > 0:
                                print('\x1b[1;31m' + 'failed' + '\x1b[0m')
                            else:
                                print('\x1b[1;32m' + 'ok' + '\x1b[0m')
                        else:
                            print()

                        failures = make_flat(results.get('failures', {}))
                        warnings = make_flat(results.get('warnings', {}))
                        skipped = make_flat(results.get('skipped', {}))
                        success = make_flat(results.get('success', {}))

                        print_if(
                            "\n".join([
                                "ERROR - {message}".format(message=r['message'])
                                for r in failures
                            ]),
                            check=verbosity>1
                        )
                        print_if(
                            "\n".join([
                                "WARNING - {message}".format(message=r['message'])
                                for r in warnings
                            ]),
                            check=verbosity>2
                        )
                        print_if(
                            "\n".join([
                                "Skipped - {message}".format(message=r['message'])
                                for r in skipped
                            ]),
                            check=verbosity>2
                        )

                        print_if(
                            "Finished - {filename}".format(filename=filename),
                            check=verbosity>1
                        )
                        print_if(
                            "\n".join([
                                "         - {num_fail} failed",
                                "         - {num_warn} warnings",
                                "         - {num_good} succeeded",
                                "         - {num_skip} skipped",
                            ]).format(
                                num_fail=len(failures),
                                num_warn=len(warnings),
                                num_skip=len(skipped),
                                num_good=len(success)
                            ),
                            check=verbosity>1
                        )
                        total_results.append(results)
                    except IOError:
                        print("Tested at WCAG2.0 %s Level" % kwargs['level'])

                print("Tested at WCAG2.0 %s Level" % kwargs['level'])
                print(
                    "{n_errors} errors, {n_warnings} warnings in {n_files} files".format(
                        n_errors=sum([len(r['failures']) for r in total_results]),
                        n_warnings=sum([len(r['warnings']) for r in total_results]),
                        n_files=len(filenames)
                    )
                )
            if sum([len(r['failures']) for r in total_results]):
                sys.exit(1)
            elif warnings_as_errors and sum([len(r['warnings']) for r in total_results]):
                sys.exit(1)
            else:
                sys.exit(0)

        return cli


def make_flat(_dict):
    return [
        r for guidelines in _dict.values()
        for techniques in guidelines.values()
        for r in techniques
    ]
