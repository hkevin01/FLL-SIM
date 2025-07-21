"""
Test suite for FLL-Sim plugin system, i18n, accessibility, logger, and error handling modules.
"""
import unittest
from fll_sim.education.plugin_system import PluginManager
from fll_sim.education.i18n import I18nManager
from fll_sim.education.accessibility import AccessibilityHelper
from fll_sim.utils.logger import FLLLogger
from fll_sim.utils.errors import FLLSimError, ConfigError, PluginError, I18nError, AccessibilityError

class TestPluginManager(unittest.TestCase):
    def test_plugin_load_and_validate(self):
        pm = PluginManager()
        pm.load_plugin('test', {'type': 'mission', 'name': 'Test Mission'})
        self.assertTrue(pm.validate_plugin('test'))
        pm.remove_plugin('test')
        self.assertNotIn('test', pm.plugins)

class TestI18nManager(unittest.TestCase):
    def test_translation(self):
        i18n = I18nManager()
        i18n.add_translation('hello', 'Hello', 'en')
        i18n.add_translation('hello', 'Hola', 'es')
        i18n.set_language('es')
        self.assertEqual(i18n.translate('hello'), 'Hola')

class TestAccessibilityHelper(unittest.TestCase):
    def test_accessibility_events(self):
        ah = AccessibilityHelper()
        ah.enable_screen_reader()
        self.assertTrue(ah.is_accessible())
        self.assertEqual(ah.get_last_event(), 'Screen reader enabled')
        ah.disable_screen_reader()
        self.assertEqual(ah.get_last_event(), 'Screen reader disabled')

class TestLogger(unittest.TestCase):
    def test_logger_info(self):
        logger = FLLLogger('test')
        logger.info('Test info message')
        self.assertTrue(hasattr(logger, 'logger'))

class TestErrors(unittest.TestCase):
    def test_custom_errors(self):
        with self.assertRaises(ConfigError):
            raise ConfigError('Config error')
        with self.assertRaises(PluginError):
            raise PluginError('Plugin error')
        with self.assertRaises(I18nError):
            raise I18nError('I18n error')
        with self.assertRaises(AccessibilityError):
            raise AccessibilityError('Accessibility error')

if __name__ == '__main__':
    unittest.main()
