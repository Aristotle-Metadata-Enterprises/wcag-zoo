from lxml import etree
import click
from wcag_zoo.utils import print_if, common_cli, common_wcag, StringIO

@common_wcag
def tarsier(filename, staticpath=".", level="AA", verbosity=1):
    """
    Tarsier reads heading levels in HTML documents (H1,H2,...H6) to verfiy order and completion against the requirements of the WCAG2.0 standard
    """

    parser = etree.HTMLParser()
    tree   = etree.parse(StringIO(html), parser)
    
    success = 0
    failed = 0
    # find all nodes that have text
    headers_xpath = " or ".join(['self::h%d'%x for x in range(7)])
    for node in tree.xpath('/html/body//*[%s]'%headers_xpath):
        print(node.tag, node.text)
            

@click.command()
@common_cli(function=tarsier)
def tarsier_cli(*args, **kwargs):
    return

if __name__ == "__main__":
    # Usage: molerat --filename="some.html" --staticpath="/home/ubuntu/workspace/mystuff" --level="AA"
    tarsier_cli()
