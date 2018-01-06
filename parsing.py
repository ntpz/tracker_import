import logging
import lxml.html


logger = logging.getLogger(__name__)


def extract_forum_ids(html, base_url):
    """ html -> [fid, ...]"""
    tree = lxml.html.fromstring(html, base_url=base_url)
    container = tree.xpath('//*[@id="forums_wrap"]/table/tr/td[1]/div[4]')[0]
    links = container.xpath(".//span[@class='sf_title']/a[@href]")
    for link in links:
        fid_str = link.attrib['href'].split("=")[1]
        yield int(fid_str)


def extract_torrents(html, base_url):
    tree = lxml.html.fromstring(html, base_url=base_url)
    rows = tree.xpath('//*[@id="main_content_wrap"]/table[@class="forumline forum"]/tr[@id]')
    for row in rows:
        try:
            yield parse_row(row)
        except SkipRow as e:
            pass


def extract_num_pages(html, base_url):
    tree = lxml.html.fromstring(html, base_url=base_url)
    page_links = tree.xpath('//*[@id="pagination"]/p[2]/a')
    if len(page_links) < 2:
        return 1
    else:
        return int(page_links[-2].text)


def parse_row(row):
    return {
        'tid': int(row.attrib['id'].split('-')[1]),
        'asize': extract_asize(row),
        'title': row.xpath('td[@class="tt"]/a')[0].text_content()
    }


def extract_asize(row):
    asize_tds = row.xpath('td[@class="tCenter med nowrap"]')

    if not asize_tds:   # no torrent size cell
        raise SkipRow()

    asize_str = asize_tds[0].text_content().strip()

    if not asize_str:       # empty torrent size cell
        raise SkipRow()

    return parse_asize(asize_str)


def parse_asize(size_str):
    size, units = size_str.strip().split('\xA0')
    if units == 'KB':
        multiplier = 1
    elif units == 'MB':
        multiplier = 1000
    elif units == 'GB':
        multiplier = 1000000
    else:
        raise ParseError("Failed to parse size from %s" % size_str)
    return int(float(size) * multiplier)


class ParseError(Exception):
    pass


class SkipRow(ParseError):
    pass
