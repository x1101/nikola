# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

import os
import uuid

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_gallery"

    def set_site(self, site):
        self.site = site
        directives.register_directive('gallery', Gallery)
        Gallery.site = site
        return super(Plugin, self).set_site(site)


class Gallery(Directive):
    """ Restructured text extension for inserting galleries."""
    has_content = True

    def run(self):
        if len(self.content) == 0:
            return

        def url_from_path(p):
            url = '/'.join(os.path.relpath(p, os.path.dirname(output_name) + os.sep).split(os.sep))
            return url

        from doit.tools import set_trace; set_trace()



        img_list = self.content.splitlines()

        photo_array = []
        for img, thumb in zip(img_list, thumbs):
            im = Image.open(thumb)
            w, h = im.size
            _image_size_cache[thumb] = w, h
            # Thumbs are files in output, we need URLs
            photo_array.append({
                'url': url_from_path(img),
                'url_thumb': url_from_path(thumb),
                'title': title,
                'size': {
                    'w': w,
                    'h': h
                },
            })

        output = self.site.template_system.render_template(
            'embedded-gallery.tmpl',
            None,
            {
                'gallery_content': self.content,
            }
        )
        return [nodes.raw('', output, format='html')]


directives.register_directive('gallery', Gallery)
