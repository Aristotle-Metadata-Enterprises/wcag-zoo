from __future__ import print_function
from lxml import etree
import click
import sys
from io import StringIO
from functools import wraps
import logging
from premailer import Premailer
import cssutils
cssutils.log.setLevel(logging.CRITICAL)


class Premoler(Premailer):
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

def print_if(*args, **kwargs):
    check = kwargs.pop('check', False)
    if check and len(args) > 0 and args[0]:
        # Only print if there is something to print
        print(*args, **kwargs)


def nice_console_text(text):
    text = text.strip().replace('\n',' ').replace('\r',' ').replace('\t',' ')
    if len(text) > 70:
        text = text[:70]+"..."
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
        style = parent.get('style',"")

        if not style:
            continue

        styles.append(dict([
            tuple(
                s.strip().split(':')
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
        'xpath' : node.getroottree().getpath(node),
        'classes': node.get('class'),
        'id': node.get('id'),
    })
    return error_dict


class WCAGCommand(object):
    """
    The base class for all WCAG validation commands
    """
    animal = None
    level = 'AA'
    
    success = 0
    failed=0
    failures = []
    warnings = []
    skipped = []
    documents = 0
    def __init__(self, *args, **kwargs):
        self.skip_these_classes = kwargs['skip_these_classes']
        self.skip_these_ids = kwargs['skip_these_ids']
        self.level = kwargs['level']
        self.kwargs = kwargs

    def add_failure(self, **kwargs):
        self.failures.append(build_msg(**kwargs))

    def add_warning(self, **kwargs):
        self.warnings.append(build_msg(**kwargs))

    def add_skipped(self, **kwargs):
        self.skipped.append(build_msg(**kwargs))

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
        skip_message = ""
        for cc in node.get('class',"").split(' '):
            if cc in self.skip_these_classes:
                skip_message.append("Skipped [%s] because node matches class [%s]\n    Text was: [%s]" % (tree.getpath(node), cc, node.text))
                skip_node = True
        if node.get('id',None) in self.skip_these_ids:
            skip_message.append("Skipped [%s] because node id is [%s]\n    Text was: [%s]" % (tree.getpath(node), node.get('id'), node.text))
            skip_node = True
        if self.skip_element(node):
            skip_node = True

        for styles in get_applicable_styles(node):
            # skip hidden elements
            if not self.kwargs.get('ignore_hidden', False):
                if "display" in styles.keys() and styles['display'].lower() == 'none':
                    skip_node = True
                if "visibility" in styles.keys() and styles['visibility'].lower() == 'hidden':
                    skip_node = True

        if skip_message:
            self.skipped.append({
                'xpath': tree.getpath(node),
                'message': "\n    ".join(skip_message),
                'classes': node.get('class'),
                'id': node.get('id'),
            })
        return skip_node

    def validate_document(self, html):
        """
        Main validation method - validates an entire document, single node from a HTML tree. Errors and warnings are attached to the classes ``failures`` and ``warnings``
        properties.

        **Note**: This checks the validatity of the whole document, but does not execute the validation loop.

        By default, returns a dictionary with the number of successful checks, and a list of failues, warnings and skipped elements.
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
        Validates an entire document from a HTML element tree. Errors and warnings are attached to the instances ``failures`` and ``warnings``
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
            html = Premoler(
                html,
                exclude_pseudoclasses=True,
                method="html",
                preserve_internal_links=True,
                base_path=self.kwargs.get('staticpath','.'),
                include_star_selectors=True,
                strip_important=False,
                disable_validation=True
            ).transform()
            parser = etree.HTMLParser()
            self._tree = etree.parse(StringIO(html), parser)
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
        @click.argument('filenames', required=True, nargs=-1)
        @click.option('--level', type=click.Choice(['AA', 'AAA', 'A']), default=None, help='WCAG level to test against. Defaults to AA.')
        @click.option('--A', 'short_level', flag_value='A', help='Shortcut for --level=A')
        @click.option('--AA', 'short_level', flag_value='AA', help='Shortcut for --level=AA')
        @click.option('--AAA', 'short_level', flag_value='AAA', help='Shortcut for --level=AAA')
        @click.option('--staticpath', default='.', help='Directory path to static files.')
        @click.option('--skip_these_classes', '-C', default="", help='Comma-separated list of CSS classes for HTML elements to *not* validate')
        @click.option('--skip_these_ids', '-I', default="", help='Comma-separated list of ids for HTML elements to *not* validate')
        @click.option('--ignore_hidden', '-H', default=False, is_flag=True, help='Validate elements that are hidden by CSS rules')
        @click.option('--animal', expose_value=False, default=False, is_flag=True, help='')
        @click.option('--warnings_as_errors', '-W', default=False, is_flag=True, help='Treat warnings as errors')
        @click.option('--verbosity', '-v', type=int, default=1, help='Specify how much text to output during processing')
        def cli(*args, **kwargs):
            total_results = []
            filenames = kwargs.pop('filenames')
            short_level = kwargs.pop('short_level', 'AA')
            kwargs['level'] = kwargs['level'] or short_level or 'AA'
            verbosity = kwargs.get('verbosity')
            warnings_as_errors = kwargs.pop('warnings_as_errors', False)
            kwargs['skip_these_classes'] = [c.strip() for c in kwargs.get('skip_these_classes').split(',') if c]
            kwargs['skip_these_ids'] = [c.strip() for c in kwargs.get('skip_these_ids').split(',') if c]
            if kwargs.pop('animal', None):
                print(__function__.animal)
                sys.exit(0)

            klass = cls(*args, **kwargs)
            for filename in filenames:
                try:
                    with open(filename) as f:
                        print_if(
                            "Starting - {filename}".format(filename=filename),
                            check=verbosity>0
                        )
                        html = f.read()
                        if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
                            html = html.decode('utf-8')
            
                        results = klass.validate_document(html)

                        print_if(
                            "\n".join([
                                "ERROR - {message}".format(message=r['message'])
                                for r in results['failures']
                            ]),
                            check=verbosity>1
                        )
                        print_if(
                            "\n".join([
                                "WARNING - {message}".format(message=r['message'])
                                for r in results['warnings']
                            ]),
                            check=verbosity>2
                        )
                        print_if(
                            "\n".join([
                                "Skipped - {message}".format(message=r['message'])
                                for r in results.get('skipped', [])
                            ]),
                            check=verbosity>2
                        )

                        print_if(
                            "Finished - {filename}".format(filename=filename),
                            check=verbosity>1
                        )
                        print_if("\n".join([
                                    "         - {num_fail} failed",
                                    "         - {num_warn} warnings",
                                    "         - {num_good} succeeded",
                                    "         - {num_skip} skipped",
                                ]).format(
                                    num_fail=len(results['failures']),
                                    num_warn=len(results['warnings']),
                                    num_skip=len(results['skipped']),
                                    num_good=results['success']
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
