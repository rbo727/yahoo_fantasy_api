#!/bin/python

import pytest
import yahoo_fantasy_api as yfa
import mock_yhandler


@pytest.fixture()
def sc():
    # For testing, we don't call out to Yahoo!  We just use a sample json file.
    # For that reason the OAuth2 session context can be None.
    yield None


@pytest.fixture()
def mock_league(sc):
    lg = yfa.League(sc, '370.l.56877')
    lg.inject_yhandler(mock_yhandler.YHandler())
    yield lg
