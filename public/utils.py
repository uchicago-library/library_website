def get_features():
    """
    Boolean fields we use as "features" in the
    spaces browse and page display.

    Returns:
        List of tuples containing three strings where
        the first item is a field name, the second item
        is a display label and the third item is an
        html icon for display.
    """
    return [
                ('is_quiet_zone', 'Quiet Zone', '<i class="fa fa-bell-slash-o"></i>'),
                ('is_collaboration_zone', 'Collaboration Zone / Group study', '<i class="material-icons">people</i>'),
                ('is_phone_zone', 'Cell Phone Zone', '<i class="material-icons">phone_android</i>'),
                ('is_meal_zone', 'Meal Zone', '<i class="material-icons">local_dining</i>'),
                ('is_open_space', 'Open Space', '<i class="material-icons">all_inclusive</i>'),
                ('is_snacks_allowed', 'Snacks allowed', '<i class="material-icons">local_cafe</i>'),
                ('is_24_hours', 'All Night Study', '<i class="material-icons">access_alarm</i>'),
                ('has_printing', 'Copy / Print / Scan', '<i class="fa fa-print"></i>'),
                ('has_public_computer', 'Public Computer(s)', '<i class="fa fa-desktop"></i>'),
                ('has_dual_monitors', 'Dual Monitor stations', '<i class="material-icons">add_to_queue</i>'),
                ('has_book_scanner', 'Overhead Book Scanner', '<i class="material-icons">import_contacts</i>'),
                ('has_screen', 'Monitor/Projector', '<i class="material-icons">cast</i>'),
                ('has_single_tables', 'Individual Tables', '<i class="material-icons">widgets</i>'),
                ('has_large_tables', 'Large Tables', '<i class="material-icons">wb_iridescent</i>'),
                ('has_carrels', 'Carrels', '<i class="material-icons">border_inner</i>'),
                ('has_standing_desk', 'Standing Desks', '<i class="material-icons">accessibility</i>'),
                ('has_soft_seating', 'Comfy Seating', '<i class="material-icons">weekend</i>'),
                ('has_board', 'White Board', '<i class="material-icons">gesture</i>'),
                ('is_reservable', 'Reservable', '<i class="fa fa-calendar-plus-o"></i>'),
                ('is_no_food_allowed', 'No Food', '<i class="fa fa-ban"></i>'),
                ('has_lockers', 'Lockers', '<i class="material-icons">lock_open</i>'),
                ('has_day_lockers', 'Day Lockers', '<i class="material-icons">lock_open</i>'),
            ]


def has_feature(feature):
    """
    See if a given feature is in the features list

    Args:
        feature: string, field name to search for.

    Returns:
        Boolean
    """
    for item in get_features():
        if item[0] == feature:
            return True
    return False


