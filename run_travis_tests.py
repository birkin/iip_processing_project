# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_travis'
    os.environ['IIP_PRC__CLONED_INSCRIPTIONS_PATH'] = 'foo'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['iip_processing_app.tests.tests_unit'])
    sys.exit(bool(failures))
