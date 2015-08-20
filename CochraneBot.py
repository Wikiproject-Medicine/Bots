import pywikibot
import re
import urllib2
ensite = pywikibot.Site('en')
aaa = u"""
[[Sinusitis]]
"""
site_url = 'https://www.ncbi.nlm.nih.gov/pubmed/'
re_update = r'<h3>Update in</h3><ul><li class="comments">' \
    '<a href="/pubmed/\d+?"'
re_update2 = r'<h3>Update in</h3><ul><li class="comments">' \
    '<a href="/pubmed/(\d+?)"'

gen = []
for name in re.findall('\[\[(.+?)\]\]', aaa):
    gen.append(pywikibot.Page(ensite, name))


def update_report(page, old_pmid, new_pmid):
    report_title = 'Wikipedia:WikiProject_Medicine/Cochrane_update'
    report = pywikibot.Page(ensite, report_title)
    report_text = report.get()
    report.text = report_text + u'\n*Article [[%s]] ([{{fullurl:%s|' \
        'action=edit}} edit]) old review [https://www.ncbi.nlm.nih.gov/' \
        'pubmed/%s PMID:%s] new review [https://www.ncbi.nlm.nih.gov/' \
        'pubmed/%s PMID:%s] - ~~~~~' \
        % (page.title(), page.title(), old_pmid, old_pmid, new_pmid, new_pmid)
    report.save('Bot: Update report')


for page in gen:
    try:
        text = page.get()
    except:
        continue
    if '<!-- No update needed -->' in text:
        continue
    pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
    print len(pmids)
    for pmid in pmids:
        res = urllib2.urlopen(
            '%s%s' % (site_url, pmid)).read().decode('utf-8')
        if 'WITHDRAWN' in res:
            continue
        if re.search(re_update, res):
            pm = re.findall(re_update2, res)[0]
            up = u'{{Update inline|reason=Updated version ' + site_url + pm
            if up not in text:
                text = re.sub(
                    ur'(\|\s*?pmid\s*?\=\s*?%s\s*?(?:\||\}\}).*?\< *?\/'
                    ur' *?ref *?\>)'
                    % pmid, ur'\1%s}}' % up, text, re.DOTALL)
            update_report(page, pmid, pm)
    if text != page.text:
        page.text = text
        page.save(u'Bot: Adding "update inline" template')
