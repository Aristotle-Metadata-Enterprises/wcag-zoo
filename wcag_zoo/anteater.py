from lxml import etree
import click
import os, sys
from wcag_zoo.utils import print_if, common_cli, common_wcag, StringIO, get_applicable_styles

# https://www.w3.org/TR/WCAG20-TECHS/H37.html
# https://www.w3.org/TR/WCAG20-TECHS/H67.html

@common_wcag
def anteater(html, staticpath=".", level="AA", verbosity=1, skip_these_classes='', skip_these_ids=''):
    """
    Anteater checks for alt and title attributes in image tags in HTML against the requirements of the WCAG2.0 standard
    """

    parser = etree.HTMLParser()
    tree   = etree.parse(StringIO(html), parser)
    
    success = 0
    failures = []
    warnings = []
    skipped = []
    # find all nodes that have text
    for node in tree.xpath('/html/body//img'):
        
        skip_node = False
        skip_message = []
        for cc in node.get('class',"").split(' '):
            if cc in skip_these_classes:
                skip_message.append("Skipped [%s] because node matches class [%s]\n    Text was: [%s]" % (tree.getpath(node), cc, node.text))
                skip_node = True
        if node.get('id',None) in skip_these_ids:
            skip_message.append("Skipped [%s] because node id class [%s]\n    Text was: [%s]" % (tree.getpath(node), node.get('id'), node.text))
            skip_node = True

        for styles in get_applicable_styles(node):
            if "display" in styles.keys() and styles['display'].lower() == 'none':
                skip_node = True

        if skip_node:
            if skip_message:
                skipped.append({
                    'xpath': tree.getpath(node),
                    'message': "\n    ".join(skip_message),
                    'classes': node.get('class'),
                    'id': node.get('id'),
                })
            continue

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
                'message': message,
                'classes': node.get('class'),
                'id': node.get('id'),
            })
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
                'message': message,
                'classes': node.get('class'),
                'id': node.get('id'),
            })
        else:
            success += 1

    return {
        "success": success,
        "failures": failures,
        "warnings": warnings,
        "skipped": []
    }

@click.command()
@common_cli(function=anteater)
def anteater_cli(*args, **kwargs):
    return

if __name__ == "__main__":
    anteater_cli()
