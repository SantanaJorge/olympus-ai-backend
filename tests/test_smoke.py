"""Smoke tests for import-time safety of the WSGI application."""

import os

from tools.env_bootstrap import strip_secret_env_vars


def test_strip_secret_env_vars_trims_openai_key():
    os.environ["OPENAI_API_KEY"] = "  sk-test\n"
    strip_secret_env_vars()
    assert os.environ["OPENAI_API_KEY"] == "sk-test"
    del os.environ["OPENAI_API_KEY"]


def test_wsgi_app_is_flask_application():
    import wsgi

    assert wsgi.app is not None
    assert wsgi.app.name is not None
