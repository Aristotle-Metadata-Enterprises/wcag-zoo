from lxml import etree
import click
from io import StringIO


@click.command()
@click.option('--filename', help='File to test for WCAG color compliance.')
@click.option('--level', help='WCAG level to test against (AAA or AA). Defaults to AA.')
@click.option('--verbosity', help='Specify how much text to output during processing')
def tarsier_cli(*args, **kwargs):
    """
    Tarsier reads heading levels in HTML documents (H1,H2,...H6) to verfiy order and completion against the requirements of the WCAG2.0 standard
    """

    results = tarsier(*args, **kwargs)
    print("\n".join([
        "Finished - {num_fail} failed",
        "         - {num_warn} warnings",
        "         - {num_good} succeeded",
        "Tested at WCAG2.0 %s Level" % kwargs['level'],
    ]).format(num_fail=len(results['failures']), num_warn=len(results['warnings']), num_good=results['success'])
    )

    if results.get('failures'):
        sys.exit(1)
    else:
        sys.exit(0)


def tarsier(filename, staticpath=".", level="AA", verbosity=1):
    if level != "AAA":
        level = "AA"
    with open(filename) as f:
        html = f.read()
        if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
            html = html.decode('utf-8')

        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(html), parser)
        
        success = 0
        failed = 0
        # find all nodes that have text
        headers_xpath = " or ".join(['self::h%d'%x for x in range(7)])
        for node in tree.xpath('/html/body//*[%s]'%headers_xpath):
            print(node.tag, node.text)
            

if __name__ == "__main__":
    # Usage: molerat --filename="some.html" --staticpath="/home/ubuntu/workspace/mystuff" --level="AA"
    tarsier_cli()
