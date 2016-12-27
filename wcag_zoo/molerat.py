from __future__ import print_function, division
from premailer import Premailer
from lxml import etree
import os, sys
import webcolors 
import click
from xtermcolor import colorize
from wcag_zoo.utils import WCAGCommand, print_if, common_cli, common_wcag, get_tree, nice_console_text, get_applicable_styles

import logging
import cssutils
cssutils.log.setLevel(logging.CRITICAL)

WCAG_LUMINOCITY_RATIO_THRESHOLD = {"AA": 4.5, "AAA": 7}

error_codes = {
}



def normalise_color(color):
    import webcolors as W
    rgba_color = None
    
    if "transparent" in color or "inherit" in color:
        rgba_color = [0,0,0,0.0]
    elif color.startswith('rgb('):
        rgba_color = map(int, color.split('(')[1].split(')')[0].split(','))
    elif color.startswith('rgba('):
        rgba_color = map(float, color.split('(')[1].split(')')[0].split(','))
    else:
        funcs = [
            W.hex_to_rgb,
            W.name_to_rgb,
            W.rgb_percent_to_rgb
        ]
        
        for func in funcs:
            try:
                rgba_color = list(func(color))
            except:
                pass

    if rgba_color is None:
        rgba_color = [0,0,0,1]
    else:
        rgba_color = (list(rgba_color) + [1])[:4]
    return rgba_color


def calculate_luminocity(r=0, g=0, b=0):
    # Calculates luminocity according to 
    # https://www.w3.org/TR/WCAG20-TECHS/G17.html#G17-tests
    
    x = []
    for C in r, g, b:
        c = C/255.0
        if c < 0.03928:
            x.append(c / 12.92)
        else:
            x.append(((c + 0.055) / 1.055) ** 2.4)
        
    R, G, B = x
    
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    return L


def generate_opaque_color(color_stack):
    # http://stackoverflow.com/questions/10781953/determine-rgba-colour-received-by-combining-two-colours

    colors = []
    # Take colors back off the stack until we get one with an alpha of 1.0
    for c in color_stack[::-1]:
        if int(c[3]) == 0:
            continue
        colors.append(c)
        if c[3] == 1.0:
            break

    red, green, blue, alpha = colors[0]

    for r, g, b, a in colors[1:]:
        if a == 0:
            # Skip transparent colors
            continue
        da = 1 - a
        alpha = alpha + a * da
        red   = (red * 0.25 + r * a * da) / alpha
        green = (green * 0.25 + g * a * da) / alpha
        blue  = (blue * 0.25 + b * a * da) / alpha

    return [int(red), int(green), int(blue)]


def calculate_luminocity_ratio(foreground, background):
    L2, L1 = sorted([
        calculate_luminocity(*foreground),
        calculate_luminocity(*background),
    ])

    return (L1 + 0.05) / (L2 + 0.05)

@common_wcag
def molerat(html, staticpath=".", level="AA", verbosity=1, skip_these_classes=[], skip_these_ids=[]):
    """
    Molerat checks color contrast in a HTML string against the WCAG2.0 standard
    
    It checks foreground colors against background colors taking into account
    opacity values and font-size to conform to WCAG2.0 Guidelines 1.4.3 & 1.4.6.
    
    However, it *doesn't* check contrast between foreground colors and background images.
    
    Paradoxically:

      a failed molerat check doesn't mean your page doesn't conform to WCAG2.0
      
      but a successful molerat check doesn't mean your page will conform either...
    
    Command line tools aren't a replacement for good user testing!
    """
    
    # https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html

    denormal = Premoler(
        html,
        exclude_pseudoclasses=True,
        method="html",
        preserve_internal_links=True,
        base_path=staticpath,
        include_star_selectors=True,
        strip_important=False,
        disable_validation=True
    ).transform()

    tree = get_tree(denormal)
    
    success = 0
    failed=0
    failures = []
    warnings = []
    skipped = []
    # find all nodes that have text
    for node in tree.xpath('/html/body//*[text()!=""]'):

        if node.text is None or node.text.strip() == "":
            continue
        if node.tag in ['script','style']:
            continue

        # set some sensible defaults that we can recognise while debugging.
        colors = [[1,2,3,1]]  # Black-ish
        backgrounds = [[254,253,252,1]]  # White-ish
        fonts = ['10pt']
        
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
            if "color" in styles.keys():
                colors.append(normalise_color(styles['color']))
            if "background-color" in styles.keys():
                backgrounds.append(normalise_color(styles['background-color']))
            if "font-size" in styles.keys():
                fonts.append(styles['font-size'])

        if skip_node:
            if skip_message:
                skipped.append({
                    'xpath': tree.getpath(node),
                    'message': "\n    ".join(skip_message),
                    'classes': node.get('class'),
                    'id': node.get('id'),
                })
            continue

        ratio_threshold = WCAG_LUMINOCITY_RATIO_THRESHOLD.get(level)

        foreground = generate_opaque_color(colors)
        background = generate_opaque_color(backgrounds)
        ratio = calculate_luminocity_ratio(foreground,background)

        if ratio < ratio_threshold:
            disp_text = nice_console_text(node.text)
            message =(
                    u"Insufficient contrast ({r:.2f}) for element - {xpath}"
                    u"\n    Computed rgb values are == Foreground {fg} / Background {bg}"
                    u"\n    Text was:         {text}"
                    u"\n    Colored text was: {color_text}"
                ).format(
                    xpath=tree.getpath(node),
                    text=disp_text,
                    fg=foreground,
                    bg=background,
                    r=ratio,
                    color_text=colorize(
                        disp_text,
                        rgb = int('0x%s'%webcolors.rgb_to_hex(foreground)[1:], 16),
                        bg = int('0x%s'%webcolors.rgb_to_hex(background)[1:], 16),
                    )
                )

            failures.append({
                'guideline': '1.4.3',
                'technique': 'H37',
                'xpath': tree.getpath(node),
                'message': message,
                'classes': node.get('class'),
                'id': node.get('id'),
            })
        else:
            success += 1  # I like what you got!

    return {
        "success": success,
        "failures": failures,
        "warnings": warnings,
        "skipped": skipped
    }

class Molerat(WCAGCommand):
    """
    Molerat checks color contrast in a HTML string against the WCAG2.0 standard
    
    It checks foreground colors against background colors taking into account
    opacity values and font-size to conform to WCAG2.0 Guidelines 1.4.3 & 1.4.6.
    
    However, it *doesn't* check contrast between foreground colors and background images.
    
    Paradoxically:

      a failed molerat check doesn't mean your page doesn't conform to WCAG2.0
      
      but a successful molerat check doesn't mean your page will conform either...
    
    Command line tools aren't a replacement for good user testing!
    """

    animal = """
        
        - https://simple.wikipedia.org/wiki/Molerat
    """

    xpath = '/html/body//*[text()!=""]'

    error_codes = {
        1: "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
    }

    def skip_element(self, node):
        
        if node.text is None or node.text.strip() == "":
            return True
        if node.tag in ['script','style']:
            return True

    def validate_element(self, node):
        print(node)

        # set some sensible defaults that we can recognise while debugging.
        colors = [[1,2,3,1]]  # Black-ish
        backgrounds = [[254,253,252,1]]  # White-ish
        fonts = ['10pt']

        
        for styles in get_applicable_styles(node):
            if "color" in styles.keys():
                colors.append(normalise_color(styles['color']))
            if "background-color" in styles.keys():
                backgrounds.append(normalise_color(styles['background-color']))
            if "font-size" in styles.keys():
                fonts.append(styles['font-size'])

        ratio_threshold = WCAG_LUMINOCITY_RATIO_THRESHOLD.get(self.level)

        foreground = generate_opaque_color(colors)
        background = generate_opaque_color(backgrounds)
        ratio = calculate_luminocity_ratio(foreground,background)
        print(ratio < ratio_threshold)
        print(ratio, ratio_threshold)
        if ratio < ratio_threshold:
            disp_text = nice_console_text(node.text)
            message =(
                    u"Insufficient contrast ({r:.2f}) for element - {xpath}"
                    u"\n    Computed rgb values are == Foreground {fg} / Background {bg}"
                    u"\n    Text was:         {text}"
                    u"\n    Colored text was: {color_text}"
                ).format(
                    xpath=node.getroottree().getpath(node),
                    text=disp_text,
                    fg=foreground,
                    bg=background,
                    r=ratio,
                    color_text=colorize(
                        disp_text,
                        rgb = int('0x%s'%webcolors.rgb_to_hex(foreground)[1:], 16),
                        bg = int('0x%s'%webcolors.rgb_to_hex(background)[1:], 16),
                    )
                )

            self.add_failure(
                guideline = '1.4.3',
                technique = 'H37',
                node = node,
                message = message,
            )
        else:
            self.success += 1  # I like what you got!

if __name__ == "__main__":
    cli = Molerat.as_cli()
    cli()