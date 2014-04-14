/*
 * Copyright 2011-2014 by Emese Revfy <re.emese@gmail.com>
 * Licensed under the GPL v2, or (at your option) v3
 *
 * Homepage:
 * http://www.grsecurity.net/~ephox/dump_call_graph_plugin/
 *
 * Usage:
 * $ make clean; make; make run &> result
 * $ create_cfg/create_call_graph.py -l result -g test -o test.txt -n fn_1
 *
 * Example cfg (printk):
 * http://www.grsecurity.net/~ephox/dump_call_graph_plugin/printk_1.png
 */

#include "gcc-common.h"

int plugin_is_GPL_compatible;

static struct plugin_info dump_call_graph_plugin_info = {
	.version	= "20140415",
	.help		= "dump cfg\n",
};

static void print_function(const_tree caller, const_tree callee)
{
	expanded_location xloc;
	const char *caller_name, *callee_name;

	gcc_assert(callee != NULL_TREE);
	if (DECL_ABSTRACT_ORIGIN(callee) != NULL_TREE)
		return;
	callee_name = DECL_NAME_POINTER(callee);

	gcc_assert(caller != NULL_TREE);
	caller_name = DECL_NAME_POINTER(caller);

	xloc = expand_location(DECL_SOURCE_LOCATION(caller));
	fprintf(stderr, "DUMP_CFG:%s:%s:%s\n", caller_name, callee_name, xloc.file);
}

static void walk_functions(struct pointer_set_t *visited, const struct cgraph_node *node)
{
	struct cgraph_edge *e;
	const_tree caller;

	if (!node)
		return;
	caller = NODE_DECL(node);

	if (pointer_set_insert(visited, caller))
		return;

	for (e = node->callees; e; e = e->next_callee) {
		const struct cgraph_node *next_node;
		const_tree callee = gimple_call_fndecl(e->call_stmt);

		if (DECL_BUILT_IN(callee))
			continue;

		print_function(caller, callee);

		next_node = cgraph_get_node(callee);
		walk_functions(visited, next_node);
	}
}

static unsigned int handle_functions(void)
{
	struct cgraph_node *node;
	struct pointer_set_t *visited;

	visited = pointer_set_create();

	FOR_EACH_FUNCTION_WITH_GIMPLE_BODY(node) {
		if (DECL_BUILT_IN(NODE_DECL(node)))
			continue;
		walk_functions(visited, node);
	}

	pointer_set_destroy(visited);
	return 0;
}

#if BUILDING_GCC_VERSION >= 4009
static const struct pass_data dump_call_graph_plugin_pass_data = {
#else
static struct ipa_opt_pass_d dump_call_graph_plugin_pass = {
	.pass = {
#endif
		.type			= SIMPLE_IPA_PASS,
		.name			= "dump_call_graph_plugin",
#if BUILDING_GCC_VERSION >= 4008
		.optinfo_flags		= OPTGROUP_NONE,
#endif
#if BUILDING_GCC_VERSION >= 4009
		.has_gate		= false,
		.has_execute		= true,
#else
		.gate			= NULL,
		.execute		= handle_functions,
		.sub			= NULL,
		.next			= NULL,
		.static_pass_number	= 0,
#endif
		.tv_id			= TV_NONE,
		.properties_required	= 0,
		.properties_provided	= 0,
		.properties_destroyed	= 0,
		.todo_flags_start	= 0,
		.todo_flags_finish	= 0,
#if BUILDING_GCC_VERSION < 4009
	},
	.generate_summary		= NULL,
	.write_summary			= NULL,
	.read_summary			= NULL,
#if BUILDING_GCC_VERSION >= 4006
	.write_optimization_summary	= NULL,
	.read_optimization_summary	= NULL,
#endif
	.stmt_fixup			= NULL,
	.function_transform_todo_flags_start		= 0,
	.function_transform		= NULL,
	.variable_transform		= NULL,
#endif
};

#if BUILDING_GCC_VERSION >= 4009
namespace {
class dump_pass : public ipa_opt_pass_d {
public:
	dump_call_graph_plugin_pass() : ipa_opt_pass_d(dump_call_graph_plugin_pass_data, g, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL) {}
	unsigned int execute() { return dump_call_graph_plugin_functions(); }
};
}
#endif

static struct opt_pass *make_dump_call_graph_plugin_pass(void)
{
#if BUILDING_GCC_VERSION >= 4009
	return new dump_call_graph_plugin_pass();
#else
	return &dump_call_graph_plugin_pass.pass;
#endif
}

int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version)
{
	const char * const plugin_name = plugin_info->base_name;
	bool enable = true;
	struct register_pass_info dump_call_graph_plugin_pass_info;

	dump_call_graph_plugin_pass_info.pass			= make_dump_call_graph_plugin_pass();
	dump_call_graph_plugin_pass_info.reference_pass_name	= "increase_alignment";
	dump_call_graph_plugin_pass_info.ref_pass_instance_number	= 1;
	dump_call_graph_plugin_pass_info.pos_op			= PASS_POS_INSERT_BEFORE;

	if (!plugin_default_version_check(version, &gcc_version)) {
		error(G_("incompatible gcc/plugin versions"));
		return 1;
	}

	register_callback(plugin_name, PLUGIN_INFO, NULL, &dump_call_graph_plugin_info);
	if (enable)
		register_callback(plugin_name, PLUGIN_PASS_MANAGER_SETUP, NULL, &dump_call_graph_plugin_pass_info);

	return 0;
}
