from premailer import Premailer
from premailer.premailer import ExternalNotFoundError
import os

import codecs
class PreMoler(Premailer):
    # We have to override this because an absolute path is from root, not the curent dir.
    def _load_external(self, url):
        """loads an external stylesheet from a remote url or local path
        """
        if url.startswith('//'):
            # then we have to rely on the base_url
            if self.base_url and 'https://' in self.base_url:
                url = 'https:' + url
            else:
                url = 'http:' + url

        if url.startswith('http://') or url.startswith('https://'):
            css_body = self._load_external_url(url)
        else:
            stylefile = url
            if not os.path.isabs(stylefile):
                stylefile = os.path.abspath(
                    os.path.join(self.base_path or '', stylefile)
                )
            elif os.path.isabs(stylefile):  # <--- This is the if branch we added
                stylefile = os.path.abspath(
                    os.path.join(self.base_path or '', stylefile[1:])
                )
            if os.path.exists(stylefile):
                with codecs.open(stylefile, encoding='utf-8') as f:
                    css_body = f.read()
            elif self.base_url:
                url = urljoin(self.base_url, url)
                return self._load_external(url)
            else:
                raise ExternalNotFoundError(stylefile)

        return css_body
