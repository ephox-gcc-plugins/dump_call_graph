CC := gcc
CXX := g++
GCCPLUGINS_DIR := $(shell $(CC) -print-file-name=plugin)
PLUGIN_FLAGS += -I$(GCCPLUGINS_DIR)/include -I$(GCCPLUGINS_DIR)/include/c-family -fPIC -shared -O2 -ggdb -Wall -W
DESTDIR :=
LDFLAGS :=
PROG := dump_call_graph_plugin.so
RM := rm

CONFIG_SHELL := $(shell if [ -x "$$BASH" ]; then echo $$BASH; \
	else if [ -x /bin/bash ]; then echo /bin/bash; \
	else echo sh; fi ; fi)

PLUGINCC := $(shell $(CONFIG_SHELL) gcc-plugin.sh "$(CC)" "$(CXX)" "$(CC)")

all: $(PROG)

$(PROG):
	$(PLUGINCC) dump_call_graph_plugin.c $(PLUGIN_FLAGS) -o $@ $<

run: $(PROG)
	$(PLUGINCC) -fplugin=$(CURDIR)/$(PROG) test.c -o test

clean:
	$(RM) -f $(PROG)
	$(RM) -f test
