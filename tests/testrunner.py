from lxml import etree

def test_file(filename):
    parser = etree.HTMLParser()
    #tree = etree.parse(StringIO(html), parser)
    tree = etree.parse(filename, parser)
    root = tree.xpath("/html")[0]
    
    tests = root.get('data-wcag-test-command').split(';')
    for test in tests:
        command = test.split(' ')[0]
        kwargs = dict([t.split('=', 1) for t in test.split(' ')[1:]])
        exec("from wcag_zoo.%s import %s as test_cls"%(command, command.title()))

        instance = test_cls(**kwargs)
        with open(filename) as f:
            html = f.read()
            if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
                html = html.decode('utf-8')
            
            results = instance.validate_document(html)
            for result in results['failures']:
                print result
                assert '%s-%s'%(command, result['error_code']) in tree.xpath(result['xpath'])[0].get('data-wcag-fail-code')


if __name__ == "__main__":
    test_file("tests/html/anteater-alt-tags.html")