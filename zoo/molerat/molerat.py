from __future__ import print_function, division
from premoler import PreMoler as Premailer
from lxml import etree
import os, sys
import webcolors 
import click
from io import StringIO


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
        print(alpha)
        if a == 0:
            # Skip transparent colors
            continue
        da = 1 - a
        alpha = alpha + a * da
        red   = (red * 0.25 + r * a * da) / alpha
        green = (green * 0.25 + g * a * da) / alpha
        blue  = (blue * 0.25 + b * a * da) / alpha

    return [int(red), int(green), int(blue)]

@click.command()
@click.option('--filename', help='File to test for WCAG color compliance.')
@click.option('--staticpath', help='Directory path to static files.')
@click.option('--level', help='WCAG level to test against (AAA or AA). Defaults to AA.')
@click.option('--verbosity', help='Specify how much text to output during processing')
def molerat(filename, staticpath=".", level="AA", verbosity=1):
    """
    Molerat checks color contrast in an HTML file against the WCAG2.0 standard
    
    It checks foreground colors against background colors taking into account
    opacity values and font-size to conform to WCAG2.0 Guidelines 1.4.3 & 1.4.6.
    
    However, it *doesn't* check contrast between foreground colors and background images.
    
    Paradoxically:
      a failed molerat check doesn't mean your page doesn't conform to WCAG2.0
      but a successful molerat check doesn't mean your page will conform either...
      
      Command line tools aren't a replacement for good user testing!
    """
    # https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html
    if level != "AAA":
        level = "AA"
    with open(filename) as f:
        html = f.read()
        if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
            html = html.decode('utf-8')
        print( os.path.join(os.path.dirname(os.path.dirname(__file__))))
        denormal = Premailer(
            html,
            exclude_pseudoclasses=True,
            method="html",
            preserve_internal_links=True,
            base_path=staticpath,
            include_star_selectors=True,
            strip_important=False,
            disable_validation=True
            
        ).transform()

        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(denormal), parser)
        
        success = 0
        failed = 0
        # find all nodes that have text
        for node in tree.xpath('/html/body//*[text()!=""]'):
            if node.text is None or node.text.strip() == "":
                continue
            if node.tag in ['script','style']:
                continue

            # set some sensible defaults.
            colors = [[1,2,3,1]]  # Black-ish
            backgrounds = [[254,253,252,1]]  # White-ish
            fonts = ['10pt']
            
            for parent in node.xpath('ancestor-or-self::*[@style]'):
                
                style = parent.get('style',"")
                if not style:
                    continue

                styles = dict([
                    tuple(
                        s.strip().split(':')
                    )
                    for s in style.split(';')
                ])
                if "color" in styles.keys():
                    colors.append(normalise_color(styles['color']))
                if "background-color" in styles.keys():
                    backgrounds.append(normalise_color(styles['background-color']))
                if "font-size" in styles.keys():
                    fonts.append(styles['font-size'])

            ratio_threshold = {"AA": 4.5, "AAA": 7}.get(level)

            foreground = generate_opaque_color(colors)
            background = generate_opaque_color(backgrounds)
            L2, L1 = sorted([
                calculate_luminocity(*foreground),
                calculate_luminocity(*background),
            ])

            ratio = (L1 + 0.05) / (L2 + 0.05)

            if ratio < ratio_threshold: # or True:
                print(
                    (
                        u"Insufficient contrast ({r:.2f}) for element - {xpath}"
                        u"\n    Text was: [{text}]"
                        u"\n    Computed rgb values are == Foreground {fg} / Background {bg}"
                    ).format(
                    xpath=tree.getpath(node),
                    text=node.text,
                    fg=foreground,
                    bg=background,
                    r=ratio
                ))
                failed += 1  # Boo!! Not cool!
            else:
                success += 1  # I like what you got!

        print("\n".join([
            "Finished - {} failed".format(failed),
            "         - {} succeeded".format(success),
            "Tested at WCAG2.0 %s Level" % level,
        ]))
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # Usage: molerat --filename="some.html" --staticpath="/home/ubuntu/workspace/mystuff" --level="AA"
    molerat()
