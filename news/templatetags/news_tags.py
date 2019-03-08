import re

from django import template
from staff.models import StaffPage

register = template.Library()


@register.inclusion_tag('news/news_author.html')
def news_author(news_page):
    if news_page.author:
        author_title = news_page.author.title
        author_url = news_page.author.url
    else:
        try:
            cnetid = news_page.owner.username
            author_title = StaffPage.objects.filter(cnetid=cnetid)[0].title
            author_url = StaffPage.objects.filter(cnetid=cnetid)[0].url
        except:
            author_title = ''
            author_url = ''
    return {
        'author_title': author_title,
        'author_url': author_url
    }

@register.inclusion_tag('news/news_excerpt.html')
def news_excerpt(news_page):
    '''Output an excerpt for a Loop news page. 
    '''

    def simplify_text(s):
        # strip out every HTML tag except opening and closing <a> tags. 
        s = re.sub(r"<(?!\/?a(?=>|\s.*>))\/?.*?>", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    # get the first num_words (e.g. 50) words. 
    # don't allow unclosed anchor tags through.
    def get_excerpt_safely(words, num_words):
        excerpt_words = words[:num_words]
        opening_anchor_tag_count = sum('<a' not in word for word in excerpt_words)
        closing_anchor_tag_count = sum('</a>' not in word for word in excerpt_words)
        if opening_anchor_tag_count != closing_anchor_tag_count:
            while True:
                last_word = excerpt_words.pop()
                if not last_word:
                    break
                if '<a' in last_word:
                    break
        return ' '.join(excerpt_words)
    
    simplified_text = simplify_text(news_page.excerpt)
    if simplified_text:
        words = simplified_text.split(" ")
        excerpt = get_excerpt_safely(words, 50)
        read_more = True
    else:
        simplified_text = simplify_text(" ".join([s.render() for s in news_page.body]))
        words = simplified_text.split(" ")
        excerpt = get_excerpt_safely(words, 50)

        if len(words) > 50:
            excerpt = excerpt + "..."
            read_more = True
        else:
            read_more = False

    return {
        'excerpt': excerpt,
        'news_page': news_page,
        'read_more': read_more
    }
