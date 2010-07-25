# -*- coding: utf-8 -*-
#
import unittest
from nose import tools
from nose.plugins.skip import SkipTest

try:
    import chardet
except ImportError:
    chardet = None

from kitchen.text import misc
from kitchen.text.exceptions import ControlCharError
from kitchen.text.converters import to_unicode

import base_classes

class TestTextMisc(unittest.TestCase, base_classes.UnicodeTestData):
    def test_guess_encoding_no_chardet(self):
        # Test that unicode strings are not allowed
        tools.assert_raises(TypeError, misc.guess_encoding, self.u_spanish)

        tools.ok_(misc.guess_encoding(self.utf8_spanish, disable_chardet=True) == 'utf8')
        tools.ok_(misc.guess_encoding(self.latin1_spanish, disable_chardet=True) == 'latin1')
        tools.ok_(misc.guess_encoding(self.utf8_japanese, disable_chardet=True) == 'utf8')
        tools.ok_(misc.guess_encoding(self.euc_jp_japanese, disable_chardet=True) == 'latin1')

    def test_guess_encoding_with_chardet(self):
        # We go this slightly roundabout way because multiple encodings can
        # output the same byte sequence.  What we're really interested in is
        # if we can get the original unicode string without knowing the
        # converters beforehand
        tools.ok_(to_unicode(self.utf8_spanish,
            misc.guess_encoding(self.utf8_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.latin1_spanish,
            misc.guess_encoding(self.latin1_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.utf8_japanese,
            misc.guess_encoding(self.utf8_japanese)) == self.u_japanese)

    def test_guess_encoding_with_chardet_installed(self):
        if chardet:
            tools.ok_(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) == self.u_japanese)
        else:
            raise SkipTest('chardet not installed, euc_jp will not be guessed correctly')

    def test_guess_encoding_with_chardet_uninstalled(self):
        if chardet:
            raise SkipTest('chardet installed, euc_jp will not be mangled')
        else:
            tools.ok_(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) ==
                self.u_mangled_euc_jp_as_latin1)

    def test_str_eq(self):
        tools.ok_(misc.str_eq(self.u_japanese, self.u_japanese) == True)
        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.euc_jp_japanese) == True)
        tools.ok_(misc.str_eq(self.u_japanese, self.euc_jp_japanese) == False)
        tools.ok_(misc.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='euc_jp') == True)

    def test_process_control_chars(self):
        tools.assert_raises(TypeError, misc.process_control_chars, 'byte string')
        tools.assert_raises(ControlCharError, misc.process_control_chars,
                *[self.u_ascii_chars], **{'strategy':'strict'})
        tools.ok_(misc.process_control_chars(self.u_ascii_chars,
            strategy='ignore') == self.u_ascii_no_ctrl)
        tools.ok_(misc.process_control_chars(self.u_ascii_chars,
            strategy='replace') == self.u_ascii_ctrl_replace)

    def test_html_entities_unescape(self):
        tools.assert_raises(TypeError, misc.html_entities_unescape, 'byte string')
        tools.ok_(misc.html_entities_unescape(self.u_entity_escape) == self.u_entity)

    def test_byte_string_valid_xml(self):
        tools.ok_(misc.byte_string_valid_xml(u'unicode string') == False)

        tools.ok_(misc.byte_string_valid_xml(self.utf8_japanese))
        tools.ok_(misc.byte_string_valid_xml(self.euc_jp_japanese, 'euc_jp'))

        tools.ok_(misc.byte_string_valid_xml(self.utf8_japanese, 'euc_jp') == False)
        tools.ok_(misc.byte_string_valid_xml(self.euc_jp_japanese, 'utf8') == False)

        tools.ok_(misc.byte_string_valid_xml(self.utf8_ascii_chars) == False)

    def test_byte_string_valid_encoding(self):
        '''Test that a byte sequence is validated'''
        tools.ok_(misc.byte_string_valid_encoding(self.utf8_japanese) == True)
        tools.ok_(misc.byte_string_valid_encoding(self.euc_jp_japanese, encoding='euc_jp') == True)

    def test_byte_string_invalid_encoding(self):
        '''Test that we return False with non-encoded chars'''
        tools.ok_(misc.byte_string_valid_encoding('\xff') == False)
        tools.ok_(misc.byte_string_valid_encoding(self.euc_jp_japanese) == False)