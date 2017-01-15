from __future__ import print_function
import click
from lxml import etree
from ast import literal_eval
import sys
import os
from utils import get_wcag_class


def test_file(filename):
    parser = etree.HTMLParser()
    path = os.path.dirname(filename)
    tree = etree.parse(filename, parser)
    root = tree.xpath("/html")[0]

    tests = root.get('data-wcag-test-command').split(';')
    for test in tests:
        command = test.split(' ')[0]
        kwargs = dict([
            (t.split('=', 1)[0], literal_eval(t.split('=', 1)[1]))
            for t in test.split(' ')[1:]
        ])

        test_cls = get_wcag_class(command)
        staticpath = kwargs.pop('staticpath', None)
        if staticpath:
            kwargs['staticpath'] = os.path.join(path, staticpath)
        instance = test_cls(**kwargs)

        with open(filename) as file:
            html = file.read()

            results = instance.validate_document(html)
            for result in results['failures']:
                if '%s-%s' % (command, result['error_code']) not in tree.xpath(result['xpath'])[0].get('data-wcag-fail-code'):
                    print(" Expected failure for node %s but code not found" % results['xpath'])
                    assert False
            for result in results['warnings']:
                if '%s-%s' % (command, result['error_code']) not in tree.xpath(result['xpath'])[0].get('data-wcag-warning-code'):
                    print(" Expected warning for node %s" % results['xpath'])
                    assert False


def test_files(filenames):
    failed = 0
    for f in filenames:
        print("Testing %s ... " % f, end="")
        try:
            test_file(f)
            print('\x1b[1;32;40m' + 'ok' + '\x1b[0m')
        except:
            failed += 1
            print('\x1b[1;31;40m' + 'failed' + '\x1b[0m')
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


@click.command()
@click.argument('filenames', required=True, nargs=-1)
def runner(filenames):
    if len(filenames) == 1:
        f = filenames[0]
        print("Testing %s ... " % f, end="")
        try:
            test_file(f)
            print('\x1b[1;32;40m' + 'ok' + '\x1b[0m')
        except:
            print('\x1b[1;31;40m' + 'failed' + '\x1b[0m')
            raise
    else:
        test_files(filenames)


if __name__ == "__main__":
    runner()
