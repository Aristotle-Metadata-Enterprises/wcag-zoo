from lxml import etree
import click
import os, sys
from io import StringIO

# https://www.w3.org/TR/WCAG20-TECHS/H37.html
# https://www.w3.org/TR/WCAG20-TECHS/H67.html

@click.command()
@click.option('--filename', required=True, help='File to test')
@click.option('--level', help='WCAG level to test against (AAA or AA). Defaults to AA.')
@click.option('--verbosity', '-v', help='Specify how much text to output during processing')
def anteater_cli(*args, **kwargs):
    """
    Anteater checks for alt and title attributes in image tags in HTML against the requirements of the WCAG2.0 standard
    """

    results = anteater(*args, **kwargs)
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

def anteater(filename, staticpath=".", level="AA", verbosity=1):
    if level != "AAA":
        level = "AA"
    verbosity = int(verbosity)
    with open(filename) as f:
        html = f.read()
        if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
            html = html.decode('utf-8')

        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(html), parser)
        
        success = 0
        failures = []
        warnings = []
        # find all nodes that have text
        for node in tree.xpath('/html/body//img'):
            if node.get('alt') is None:
                message =(
                        u"Missing alt tag on image for element - {xpath}"
                        u"\n    Image was: {img_url}"
                    ).format(
                    xpath=tree.getpath(node),
                    img_url=node.get('src')
                    )

                failures.append({
                    'guideline': '1.1.1',
                    'technique': 'H37',
                    'xpath': tree.getpath(node),
                    'message': message
                })
                
                if verbosity > 0:
                    print('ERROR:   ' + message)
            elif node.get('alt') == "":
                message =(
                        u"Blank alt tag on image for element - {xpath}"
                        u"\n    Image was: {img_url}"
                        u"\n    Only use blank alt tags when an image is purely decorative."
                    ).format(
                    xpath=tree.getpath(node),
                    img_url=node.get('src')
                    )

                warnings.append({
                    'guideline': '1.1.1',
                    'technique': 'H37',
                    'xpath': tree.getpath(node),
                    'message': message
                })
                
                if verbosity > 1:
                    print('WARNING: ' + message)
            else:
                success += 1

    return {
        "success": success,
        "failures": failures,
        "warnings": warnings
    }

if __name__ == "__main__":
    anteater_cli()
