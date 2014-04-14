#!/usr/bin/env python

from sys import stderr
from optparse import OptionParser

class MissingMakeLog(Exception):
    def __init__(self):
        Exception.__init__(self)

class MissingFunctionName(Exception):
    def __init__(self):
        Exception.__init__(self)

class WrongFunction(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class PrintFunction():
    def __init__(self, functions, options):
        self.functions = functions
        self.start_fn = options.fn
        self.count = 0
        self.graph = None

        if options.image:
            self.graph = self.image_name = options.image

        if options.out:
            self.output = open(options.out, 'w')
        else:
            self.output = None

        self.ident = 0
        self.separator = ' '
        self.cur_parent = self.start_fn

    def __init_image_drawing(self):
        if not self.graph:
            return

        try:
            import pygraphviz as PG
        except ImportError:
            stderr.write("emerge dev-python/pygraphviz\n\n")
            raise ImportError

        self.count += 1
        self.image_name += '_%u.png' % self.count

        self.graph = PG.AGraph(directed=True, strict=True)
        self.graph.add_node(self.start_fn)

    def __create_image(self):
        if not self.graph:
            return

        self.graph.layout(prog='dot')
        self.graph.draw(self.image_name)

    def __init_scope(self, file):
        self.scope = file

    def __set_scope(self, fn):
        if len(self.functions[fn]) != 1:
            return
        if fn == self.start_fn:
            return
        file = self.functions[fn].keys()[0]
        self.__init_scope(file)

    def __init_visited(self):
        self.visited_fns = {}

    def __is_visited(self, fn):
        if self.visited_fns.has_key(fn) and self.visited_fns[fn] == self.scope:
            return True
        self.visited_fns[fn] = self.scope
        return False

    def __print_out(self, str):
        if self.output:
            self.output.write(str)
        elif not self.graph:
            print str

    def __print_function(self, fn, ident):
        if self.graph and fn != self.start_fn:
            self.graph.add_node(fn)
            self.graph.add_edge(self.cur_parent, fn)

        num = 0
        sep = ''
        while ident != num:
            sep += self.separator
            num += 1

        self.__print_out(sep + fn + '\n')

    def __walk_functions(self, fn, ident):
        self.__print_function(fn, ident)

        if not self.functions.has_key(fn):
            return
        if self.__is_visited(fn):
            return

        self.__set_scope(fn)
        if not self.functions[fn].has_key(self.scope):
            return

        for child in self.functions[fn][self.scope]:
            self.cur_parent = fn
            self.__walk_functions(child, ident + 1)

    def print_cfg(self):
        if not self.functions.has_key(self.start_fn):
            raise WrongFunction(self.start_fn)

        for file in self.functions[self.start_fn].iterkeys():
            self.__init_scope(file)
            self.__init_visited()
            self.__init_image_drawing()

            self.__print_out('---------------- start: %s():%s ----------------\n' % (self.start_fn, self.scope))
            self.__walk_functions(self.start_fn, 0)
            self.__print_out('\n')
            self.__create_image()

        if self.output:
            self.output.close()

def parse_make_log(options):
    functions = {}

    for line in open(options.log, 'r'):
        if not line.startswith('DUMP_CFG'):
            continue

        data = line.split(':')
        parent = data[1]
        child = data[2]
        file = data[3]
        if file[-1] == '\n':
            file = file[:-1]

        try:
            functions[parent][file].append(child)
        except KeyError:
            if not functions.has_key(parent):
                functions[parent] = {file : [child]}
            else:
                functions[parent][file] = [child]

    return functions

def main(parser):
    (options, _) = parser.parse_args()

    if not options.log:
        parser.print_help()
        raise MissingMakeLog
    if not options.fn:
        parser.print_help()
        raise MissingFunctionName

    functions = parse_make_log(options)

    print_fns_obj = PrintFunction(functions, options)
    print_fns_obj.print_cfg()

if __name__ == '__main__':
    parser = OptionParser(usage='%prog -l make_log -n SyS_ioctl', version='%prog 0.0.1')
    parser.add_option('-g', '--create_image', dest='image', help='create an image from the cfg (image file name)')
    parser.add_option('-l', '--log', dest='log', help='output of the make')
    parser.add_option('-n', '--name', dest='fn', help='create cfg of this function')
    parser.add_option('-o', '--output', dest='out', help='name of the output file')

    main(parser)
