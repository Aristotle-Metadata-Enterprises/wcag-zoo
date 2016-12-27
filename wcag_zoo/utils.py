from __future__ import print_function
from lxml import etree
import click
import sys
from io import StringIO
from functools import wraps

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


def get_tree(html):
    parser = etree.HTMLParser()
    return etree.parse(StringIO(html), parser)


def build_msg(**kwargs):
    node = kwargs.pop('node')
    error_dict = kwargs
    error_dict.update({
        'xpath' : node.getroottree().getpath(node),
        'classes': node.get('class'),
        'id': node.get('id'),
    })
    return error_dict


def common_cli(function):
    
    __function__ = function
    @wraps(__function__)
    def wrapper(function):
        
        @click.argument('filenames', required=True, nargs=-1)
        @click.option('--level', type=click.Choice(['AA', 'AAA', 'A']), default=None, help='WCAG level to test against. Defaults to AA.')
        @click.option('--A', 'short_level', flag_value='A', help='Shortcut for --level=A')
        @click.option('--AA', 'short_level', flag_value='AA', help='Shortcut for --level=AA')
        @click.option('--AAA', 'short_level', flag_value='AAA', help='Shortcut for --level=AAA')
        @click.option('--skip_these_classes', '-C', default="", help='Comma-separated list of CSS classes for HTML elements to *not* validate')
        @click.option('--skip_these_ids', '-I', default="", help='Comma-separated list of ids for HTML elements to *not* validate')
        @click.option('--animal', expose_value=False, default=False, is_flag=True, help='')
        @click.option('--warnings_as_errors', '-W', default=False, is_flag=True, help='Treat warnings as errors')
        @click.option('--verbosity', '-v', type=int, default=1, help='Specify how much text to output during processing')
        def cli(*args, **kwargs):
            total_results = []
            filenames = kwargs.pop('filenames')
            kwargs['level'] = kwargs['level'] or kwargs['short_level'] or 'AA'
            verbosity = kwargs.get('verbosity')
            warnings_as_errors = kwargs.pop('warnings_as_errors', False)
            kwargs['skip_these_classes'] = [c.strip() for c in kwargs.get('skip_these_classes').split(',') if c]
            kwargs['skip_these_ids'] = [c.strip() for c in kwargs.get('skip_these_ids').split(',') if c]
            if kwargs.pop('animal', None):
                print(__function__.animal)
                sys.exit(0)

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
            
                        results = __function__(html, **kwargs)

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
    return wrapper

def common_wcag(animal=""):
    def dec(function):
        @wraps(function)
        def inner(*args, **kwargs):
            assert kwargs.get('level',"B") in 'AAA', "WCAG level must be 'A', 'AA' or 'AAA'"
            return function(*args, **kwargs)
        inner.animal = animal
        return inner
    return dec

class WCAGCommand(object):
    animal = None
    
    success = 0
    failed=0
    failures = []
    warnings = []
    skipped = []
    documents = 0
    def __init__(self, *args, **kwargs):
        self.skip_these_classes = kwargs['skip_these_classes']
        self.skip_these_ids = kwargs['skip_these_ids']
        self.kwargs = kwargs

    def add_failure(self, **kwargs):
        self.failures.append(build_msg(**kwargs))

    def add_warning(self, **kwargs):
        self.warnings.append(build_msg(**kwargs))

    def add_skipped(self, **kwargs):
        self.skipped.append(build_msg(**kwargs))

    def skip_element(self, node):
        return ""

    def _check_skip_element(self, node):
        skip_node = False
        skip_message = ""
        for cc in node.get('class',"").split(' '):
            if cc in self.skip_these_classes:
                skip_message.append("Skipped [%s] because node matches class [%s]\n    Text was: [%s]" % (tree.getpath(node), cc, node.text))
                skip_node = True
        if node.get('id',None) in self.skip_these_ids:
            skip_message.append("Skipped [%s] because node id class [%s]\n    Text was: [%s]" % (tree.getpath(node), node.get('id'), node.text))
            skip_node = True
        if self.skip_element(node):
            skip_message.append(self.skip_element(node))
            skip_node = True

        for styles in get_applicable_styles(node):
            if "display" in styles.keys() and styles['display'].lower() == 'none':
                # skip hidden elements
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
        self.tree = self.get_tree(html)
        self.run_validation_loop()

        return {
            "success": self.success,
            "failures": self.failures,
            "warnings": self.warnings,
            "skipped": self.skipped
        }

    def validate_whole_document(self, html):
        pass
        
    def validate_element(self, elem):
        pass

    def get_tree(self, html):
        parser = etree.HTMLParser()
        return etree.parse(StringIO(html), parser)

    def run_validation_loop(self, xpath=None, validator=None):
        if xpath is None:
            xpath = self.xpath
        for element in self.tree.xpath(xpath):
            if self._check_skip_element(element):
                continue
            if not validator:
                self.validate_element(element)
            else:
                validator(element)

    def validate_files(self, *files):
        pass

    @classmethod
    def as_cli(cls):

        @click.command(help=cls.__doc__)
        @click.argument('filenames', required=True, nargs=-1)
        @click.option('--level', type=click.Choice(['AA', 'AAA', 'A']), default=None, help='WCAG level to test against. Defaults to AA.')
        @click.option('--A', 'short_level', flag_value='A', help='Shortcut for --level=A')
        @click.option('--AA', 'short_level', flag_value='AA', help='Shortcut for --level=AA')
        @click.option('--AAA', 'short_level', flag_value='AAA', help='Shortcut for --level=AAA')
        @click.option('--skip_these_classes', '-C', default="", help='Comma-separated list of CSS classes for HTML elements to *not* validate')
        @click.option('--skip_these_ids', '-I', default="", help='Comma-separated list of ids for HTML elements to *not* validate')
        @click.option('--animal', expose_value=False, default=False, is_flag=True, help='')
        @click.option('--warnings_as_errors', '-W', default=False, is_flag=True, help='Treat warnings as errors')
        @click.option('--verbosity', '-v', type=int, default=1, help='Specify how much text to output during processing')
        def cli(*args, **kwargs):
            total_results = []
            filenames = kwargs.pop('filenames')
            short_level = kwargs.pop('short_level', 'AA')
            kwargs['level'] = kwargs['level'] or short_level
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
