import os
import re
from typing import Any

import scrapy
from scrapy.http import Response

from docspider.items import DocspiderItem
from markdownify import markdownify as md


class ReadTheDocsSpider(scrapy.Spider):
    name = "flask"
    allowed_domains = ["python-adv-web-apps.readthedocs.io", "flask.palletsprojects.com", "docs.godotengine.org", "readthedocs.io"]
    start_urls = ["https://flask.palletsprojects.com/en/3.0.x/"]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        Parses the given response object and extracts URLs from the href attributes from the anchor tags.

        Args:
            response (Response): The response object containing the HTML content.

        Returns:
            Any: A generator that yields scrapy.Request objects for each extracted URL.
        """
        if not os.path.exists(f"data/{self.name}"):
            os.makedirs(f"data/{self.name}")

        for href in response.css("ul > li > a::attr('href')"):
            s = href.extract()
            # Skip internal links
            if s.startswith('#') or not s:
                continue
            url = response.urljoin(s)
            yield scrapy.Request(url, callback=self.markdownify_response)

    def markdownify_response(self, response: Response):
        item = DocspiderItem()
        s = md(response.text, strip=['a', 'ul', 'li']).strip()
        s = re.sub(r'\n+', '\n\n', s)
        s = s.replace('\\_', '_')

        item_title = s[0:s.find('\n')]

        i = s.find('===')
        if i != -1:
            i += s[i:].find('\n')
            s = s[i:]
        item['markdown'] = s
        item['url'] = response.url
        item['name'] = item_title

        # Save markdown in data/{name}
        # Make dir if not exists

        fname = item_title.replace(" ", "_")
        with open(f"data/{self.name}/{fname}.md", "w") as f:
            f.write(s)

        yield item