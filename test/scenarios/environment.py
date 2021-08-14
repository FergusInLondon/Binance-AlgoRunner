from unittest.mock import patch

def before_feature(context, feature):
    if 'mock_logger' in feature.tags:
        context._mock_logger = patch("algorunner.hooks.logger")
        context.mock_logger = context._mock_logger.__enter__()

def after_feature(context, feature):
    if 'mock_logger' in feature.tags:
        context._mock_logger.__exit__((None,))
