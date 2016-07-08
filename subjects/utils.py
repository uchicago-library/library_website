import urllib.parse

SUBJECT_BROWSE_URL = '/collex/?view=subjects&amp;subject='

def get_subjects_html(subjects):
    """
    Generate an html list of subjects that 
    link to back to their respective places
    in the subjects browse.

    Args:
        subjects: object, django QuerySet 
        <class 'django.db.models.query.QuerySet'>

    Returns:
        String, html with subjects as anchors 
        linking into the subject browse.
    """
    html = ''
    for s in subjects:
        subject = str(s.subject)
        param = urllib.parse.quote_plus(subject)
        html += '<a href="%s">%s</a><br/>' % (SUBJECT_BROWSE_URL + param, subject)
    return  html
