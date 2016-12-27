from __future__ import print_function
import click
import sys
from io import StringIO
from functools import wraps

def print_if(*args, **kwargs):
    check = kwargs.pop('check', True)
    if check:
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


def common_cli(function,*args, **kwargs):
    
    __function__ = function
    @wraps(__function__)
    def inner(function):
        
        @click.argument('filenames', required=True, nargs=-1)
        @click.option('--level', type=click.Choice(['AA', 'AAA', 'A']), default='AA', help='WCAG level to test against. Defaults to AA.')
        @click.option('--verbosity', '-v', type=int, default=1, help='Specify how much text to output during processing')
        @click.option('--AA', default=False, is_flag=True, help='Shortcut for --level=AA')
        @click.option('--AAA', default=False, is_flag=True, help='Shortcut for --level=AAA')
        @click.option('--skip_these_classes', '-C', default="", help='Comma-separated list of CSS classes for HTML elements to *not* validate')
        @click.option('--skip_these_ids', '-I', default="", help='Comma-separated list of ids for HTML elements to *not* validate')
        def cli(*args, **kwargs):
            total_results = []
            filenames = kwargs.pop('filenames')
            verbosity = kwargs.get('verbosity')
            wcag_aa = kwargs.pop('aa', False)
            wcag_aaa = kwargs.pop('aaa', False)
            kwargs['skip_these_classes'] = [c.strip() for c in kwargs.get('skip_these_classes').split(',') if c]
            kwargs['skip_these_ids'] = [c.strip() for c in kwargs.get('skip_these_ids').split(',') if c]

            if wcag_aa:
                kwargs['level'] = 'AA'
            elif wcag_aaa:
                kwargs['level'] = 'AAA'
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
                "{n_errors} errors, {n_warnings} in {n_files} files".format(
                    n_errors=sum([len(r['failures']) for r in total_results]),
                    n_warnings=sum([len(r['warnings']) for r in total_results]),
                    n_files=len(filenames)
                )
            )
            if sum([len(r['failures']) for r in total_results]):
                sys.exit(1)
            else:
                sys.exit(0)
        return cli
    return inner

def common_wcag(function):
    @wraps(function)
    def inner(*args, **kwargs):
        
        assert kwargs.get('level',None) in 'AAA', "WCAG level must be 'A', 'AA' or 'AAA'"
        return function(*args, **kwargs)

    return inner
