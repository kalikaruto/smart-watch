
import logging
import coloredlogs

def setup_logging():
    """Sets up the root logger with colored output."""
    level_styles = {
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'red', 'bold': True},
    }

    field_styles = coloredlogs.DEFAULT_FIELD_STYLES
    field_styles['levelname'] = {'color': 'white', 'bold': True}

    coloredlogs.install(
        level='INFO',
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        level_styles=level_styles,
        field_styles=field_styles
    )

# Set up the logger immediately when this module is imported
setup_logging()
