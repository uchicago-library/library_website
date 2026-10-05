def get_first_feature_story():
    """
    Get the most recent published feature story.

    Returns:
        LibNewsPage object.
    """
    from .models import LibNewsPage

    feature = (
        LibNewsPage.objects.live()
        .filter(is_feature_story=True)
        .order_by("-published_at")
        .first()
    )
    return feature
