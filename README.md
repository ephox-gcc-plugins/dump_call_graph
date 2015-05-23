dump_call_graph
===============

Print out the call graph.

Example cfg (printk):
http://www.grsecurity.net/~ephox/dump_call_graph_plugin/printk_1.png

Compiling & Usage
-----------------

##### gcc 4.5 - 5:
```shell
$ make clean; make run &> result
$ create_cfg/create_call_graph.py -l result -g test -o test.txt -n fn_1
```
