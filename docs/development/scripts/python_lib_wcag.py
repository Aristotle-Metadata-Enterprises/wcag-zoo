#!/usr/bin/env python3
from wcag_zoo.validators.tarsier import Tarsier

my_html = b"<html><head><body><h1>1</h1><h3>This is wrong, it should be h2"
instance = Tarsier()
results = instance.validate_document(my_html)

print("/no/tmp/dir", len(results['failures']), "failures")
