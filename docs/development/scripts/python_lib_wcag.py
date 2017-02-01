#!/usr/bin/env python2
from wcag_zoo.validators.tarsier import Tarsier

my_html = "<html><head><body><h2>This is wrong, it should be h1"
instance = Tarsier()
results = instance.validate_document(my_html)

print "/no/tmp/dir", len(results['failures']), "failures"
