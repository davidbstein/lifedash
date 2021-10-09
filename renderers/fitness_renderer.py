import datetime
from .templates import (
    FITNESS_BAR_TEMPLATE
)


def render_fitness_bar(garmin_data):
    #['activities', 'sleeps', 'epochs', 'dailies', 'bodyComps', 'userMetrics']
    return FITNESS_BAR_TEMPLATE.format({})
