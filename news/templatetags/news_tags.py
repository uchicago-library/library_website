import re

from django import template

from staff.models import StaffPage

register = template.Library()


@register.inclusion_tag("news/news_author.html")
def news_author(news_page):
    if news_page.author:
        author_title = news_page.author.title
        author_url = news_page.author.url
    else:
        try:
            cnetid = news_page.owner.username
            author_title = StaffPage.objects.filter(cnetid=cnetid)[0].title
            author_url = StaffPage.objects.filter(cnetid=cnetid)[0].url
        except:  # noqa: E722
            author_title = ""
            author_url = ""
    return {"author_title": author_title, "author_url": author_url}


@register.inclusion_tag("news/news_excerpt.html")
def news_excerpt(news_page):
    """
    Output an excerpt for a Loop news page.
    """

    def simplify_text(s):
        # strip out every HTML tag except opening and closing <a> tags.
        s = re.sub(r"<(?!\/?a(?=>|\s.*>))\/?.*?>", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    if simplify_text(news_page.excerpt):
        excerpt = news_page.excerpt
        richtext = True
    else:
        excerpt = news_page.body
        richtext = False

    return {"excerpt": excerpt, "news_page_url": news_page.url, "rt": richtext}
