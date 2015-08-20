from pywikibot import pagegenerators
import pywikibot
import mwparserfromhell
import re
import codecs
site = pywikibot.Site('en')
summary = 'Bot: Deprecating [[Template:Cite pmid]] and some minor fixations'
with codecs.open('/data/project/dexbot/core-git/med.txt', 'r', 'utf-8') as f:
    med_arts = set(f.read().split('\n'))


def fix_infobox(text):
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name.startswith('infobox'):
            infobox = template
            break
    else:
        return text
    new = unicode(infobox)
    for param in infobox.params:
        if '\n' in param.name and '\n' not in param.value:
            new_param = param
            new_param.name = new_param.name.replace('\n', '')
            new_param.value = new_param.value + ' \n'
            new = new.replace(unicode(param), unicode(new_param))
    new_text = text.replace(unicode(infobox), new)
    return new_text


def fix_cite(text):
    new_text = text
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name.lower().startswith('cite '):
            new_text = new_text.replace(
                unicode(template),
                re.sub(ur'\n(\s*?(?:\||\}\}))', ur'\1', unicode(template)))
    return new_text


def fix_cite_pmid(text):
    new_text = text
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name.lower().startswith('cite pmid'):
            pmid = template.get(1).value
            if not pmid:
                continue
            pmid_page = pywikibot.Page(site, 'Template:Cite pmid/%s' % pmid)
            if pmid_page.isRedirectPage():
                pmid_page = pmid_page.getRedirectTarget()
            try:
                pmid_text = pmid_page.get()
            except pywikibot.NoPage:
                continue
            pmid_text = pmid_text.split('<noinclude')[0]
            template_text = unicode(template)
            new_text = new_text.replace(template_text, pmid_text)
    if new_text == text:
        raise RuntimeError(re.findall(ur'\{\{[Cc]ite pmid.+?\}\}', text))
    return new_text


gen = pagegenerators.ReferringPageGenerator(
    pywikibot.Page(site, u"Template:Cite pmid"), onlyTemplateInclusion=True)
pregen = pagegenerators.PreloadingGenerator(gen)
c = 0
for page in pregen:
    if not page.title().replace(' ', '_') in med_arts:
        continue
    if c > 20:
        pass
        # break
    page_text = page.get()
    try:
        new_text = fix_cite_pmid(page_text)
    except:
        continue
    c += 1
    new_text = fix_cite(new_text)
    new_text = fix_infobox(new_text)
    page.put(new_text, summary)
