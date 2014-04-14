#!/usr/bin/env python

import unittest, os, filecmp

from create_call_graph import *

test_data = 'test_data'

class TestParser():
    def __init__(self, log='%s/log' % test_data, fn='fn_1', out=None):
        self.options = TestOption(log, fn, out)

    def parse_args(self):
        return (self.options, None)

    def print_help(self):
        pass

class TestOption():
    def __init__(self, log='%s/log' % test_data, fn='fn_1', out=None):
        self.log = log
        self.fn = fn
        self.out = out
        self.image = None

class TestCreateCfg(unittest.TestCase):
    def setUp(self):
        self.tmpf = 'out'
        self.input_1 = {'fn_4': {'test.c': ['fn_5'], 'test_nyuszi.c': ['fn_10']}, 'fn_1': {'test.c': ['fn_4', 'fn_3', 'fn_2'], 'test_nyuszi.c': ['fn_4']}}

        self.log = '%s/log' % test_data
        self.log_expect = '%s_out' % self.log

        self.log_extern = '%s/log_with_extern' % test_data
        self.log_extern_expect = '%s_out' % self.log_extern

        self.log_big = '%s/log_big' % test_data
        self.log_big_expect = '%s_out' % self.log_big

        self.log_dup = '%s/log_dup_fns' % test_data
        self.log_dup_expect = '%s_out' % self.log_dup

        self.log_dup_2 = '%s/log_dup_2' % test_data
        self.log_dup_2_expect = '%s_out' % self.log_dup_2

    def test_main_missing_args(self):
        args = TestParser(log=None)
        with self.assertRaises(MissingMakeLog):
            main(args)

        args = TestParser(fn=None)
        with self.assertRaises(MissingFunctionName):
            main(args)

    def test_parse_make_log(self):
        options = TestOption(log=self.log_dup)

        self.assertEqual(parse_make_log(options), self.input_1)

    def test_good_log(self):
        args = TestParser(log=self.log, out=self.tmpf)
        main(args)

        self.assertTrue(filecmp.cmp(self.tmpf, self.log_expect))

    def test_extern_log(self):
        args = TestParser(log=self.log_extern, out=self.tmpf)
        main(args)

        self.assertTrue(filecmp.cmp(self.tmpf, self.log_extern_expect))

    def test_big_log(self):
        args = TestParser(log=self.log_big, fn='SyS_ioctl', out=self.tmpf)
        main(args)

        self.assertTrue(filecmp.cmp(self.tmpf, self.log_big_expect))

    def test_wrong_fn(self):
        options = TestOption(fn='asdadsasdadasd', out=self.tmpf)
        functions = parse_make_log(options)
        print_fns_obj = PrintFunction(functions, options)

        with self.assertRaises(WrongFunction):
            print_fns_obj.print_cfg()

    def test_dup_fn_make_log(self):
        options = TestOption(log=self.log_dup, out=self.tmpf)

        functions = parse_make_log(options)
        print_fns_obj = PrintFunction(functions, options)
        print_fns_obj.print_cfg()

        self.assertTrue(filecmp.cmp(self.tmpf, self.log_dup_expect))

    def test_dup_log_2(self):
        options = TestOption(log=self.log_dup_2, out=self.tmpf)

        functions = parse_make_log(options)
        print_fns_obj = PrintFunction(functions, options)
        print_fns_obj.print_cfg()

        self.assertTrue(filecmp.cmp(self.tmpf, self.log_dup_2_expect))

    def tearDown(self):
        if os.path.isfile('out'):
            os.remove('out')


if __name__ == '__main__':
    unittest.main()
