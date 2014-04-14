#/bin/bash

# python -m unittest test_kernel_hash_table_generator.TestKernelMake.test_kernel_make_two_make

python -m unittest -f -v test_create_call_graph
if [ $? -ne 0 ]; then
	echo "FAILED: test_create_call_graph"
	exit 1
fi

echo "------------------------------------------------------------------------------------------------"
if [ ! `which coverage-2.7` >/dev/null ]; then
	echo "emerge dev-python/coverage"
	exit 0
fi

coverage-2.7 -x test_create_call_graph.py
coverage-2.7 -rm create_call_graph.py
