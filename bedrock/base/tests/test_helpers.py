# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.test import TestCase, override_settings

from django_jinja.backend import Jinja2
from mock import patch

from bedrock.base.templatetags import helpers

jinja_env = Jinja2.get_default()
SEND_TO_DEVICE_MESSAGE_SETS = {
    "default": {
        "email": {
            "android": "download-firefox-android",
            "ios": "download-firefox-ios",
            "all": "download-firefox-mobile",
        }
    }
}


def render(s, context={}):
    t = jinja_env.from_string(s)
    return t.render(context)


class HelpersTests(TestCase):
    def test_urlencode_with_unicode(self):
        template = '<a href="?var={{ key|urlencode }}">'
        context = {"key": "?& /()"}
        assert render(template, context) == '<a href="?var=%3F%26+%2F%28%29">'
        # non-ascii
        context = {"key": "\xe4"}
        assert render(template, context) == '<a href="?var=%C3%A4">'

    def test_mailtoencode_with_unicode(self):
        template = '<a href="?var={{ key|mailtoencode }}">'
        context = {"key": "?& /()"}
        assert render(template, context) == '<a href="?var=%3F%26%20/%28%29">'
        # non-ascii
        context = {"key": "\xe4"}
        assert render(template, context) == '<a href="?var=%C3%A4">'


@override_settings(LANG_GROUPS={"en": ["en-US", "en-GB"]})
def test_switch():
    with patch.object(helpers, "waffle") as waffle:
        ret = helpers.switch({"LANG": "de"}, "dude", ["fr", "de"])

    assert ret is waffle.switch.return_value
    waffle.switch.assert_called_with("dude")

    with patch.object(helpers, "waffle") as waffle:
        assert not helpers.switch({"LANG": "de"}, "dude", ["fr", "en"])

    waffle.switch.assert_not_called()

    with patch.object(helpers, "waffle") as waffle:
        ret = helpers.switch({"LANG": "de"}, "dude")

    assert ret is waffle.switch.return_value
    waffle.switch.assert_called_with("dude")

    with patch.object(helpers, "waffle") as waffle:
        ret = helpers.switch({"LANG": "en-GB"}, "dude", ["de", "en"])

    assert ret is waffle.switch.return_value
    waffle.switch.assert_called_with("dude")


@override_settings(DONATE_PARAMS={"en-US": {"presets": "50,30,20,10"}, "id": {"presets": "270000,140000,70000,40000"}})
class TestGetDonateParams(TestCase):
    def test_en_us(self):
        ctx = {"LANG": "en-US"}
        params = helpers.get_donate_params(ctx)
        assert params["preset_list"] == "50,30,20,10".split(",")

    def test_id(self):
        ctx = {"LANG": "id"}
        params = helpers.get_donate_params(ctx)
        assert params["preset_list"] == "270000,140000,70000,40000".split(",")

    def test_undefined_locale(self):
        ctx = {"LANG": "de"}
        params = helpers.get_donate_params(ctx)
        assert params["preset_list"] == "50,30,20,10".split(",")
