import re
import os
from shutil import rmtree

# constraints:
# I >= (N+1)*K/2 + 5 && I <= 140
# K*N%lane_num == 0 && I%lane_num == 0 && lane_num >=1 && lane_num <= N
# lim_size*I >= 0.5*(channel_width/2)*4 && lim_size*I <= 2*(channel_width/2)*4
# 96 40*8

K = 6
N = 8
lane_num = 4
I = 40
wires = [(1, 4), (2, 1), (4, 2), (6, 1)]
channel_width = sum(length * num * 2 * N for length, num in wires)
local_routing_param_comb = []
print(channel_width)

# generate local routing parameters combination
# for lane_num in (2, 3, 4, 6, 8):
lane_num = 1
for I in range((N + 1) * K // 2 + 5, 81):
    if I % 4 == 0:
        if (K * N) % lane_num == 0 and I % lane_num == 0:
            for lim_size in range(4, 25, 2):
                if lim_size * I <= 640:
                    if lim_size % 2 == 1:
                        continue
                    comb = (lane_num, I, lim_size)
                    local_routing_param_comb.append(comb)

# generate globe switch pattern combination
local_routing_pat = re.compile(r"%local_routing%")
local_routing_template = '<local_routing K="6" N="8" lane_num="%d" I="%d" O="16" fd="0.5" interlane_con_dir="1">\n\t<LIM mux_size="%d"/>\n\t<LEIM full_crossbar="1"/>\n</local_routing>'
global_routing_pat = re.compile(r"%topology%")

topology_names = []
topology_name = ''
for output in ('o_16', 'o_12', 'o_14'):
    topology_name = output + '__' + '12_i' + '__' + '6_1__4_1__2_1'
    if output == 'o_12':
        topology_names.append(topology_name + '__2_4__2_6')
        topology_names.append(topology_name + '__2_4__2_6__4_6')
    elif output == 'o_14':
        topology_names.append(topology_name + '__4_2__4_6')
        topology_names.append(topology_name + '__4_2__4_6__2_6')
    elif output == 'o_16':
        topology_names.append(topology_name + '__6_2__6_4')
        topology_names.append(topology_name + '__6_2__6_4__2_4')
    else:
        exit(-1)
rule_template = '<rule source="%s" sink="%s"/>'
topologies = {}
for topology_name in topology_names:
    rules = []
    for rule in topology_name.split('__'):
        if rule.startswith('o'):
            rules.append(rule_template % ('O', 'L%s'%rule.split('_')[1][0]))
            rules.append(rule_template % ('O', 'L%s'%rule.split('_')[1][1]))
        elif rule.endswith('i'):
            rules.append(rule_template % ('L%s'%rule.split('_')[0][0], 'I'))
            rules.append(rule_template % ('L%s'%rule.split('_')[0][1], 'I'))
        else:
            rules.append(rule_template % ('L%s'%rule.split('_')[0],'L%s'%rule.split('_')[1]))
    rules.append(rule_template % ('L6', 'L1'))
    rules.append(rule_template % ('L4', 'L1'))
    rules.append(rule_template % ('L2', 'L1'))
    rules.append(rule_template % ('L1', 'L1'))
    rules.append(rule_template % ('L6', 'L6'))
    rules.append(rule_template % ('L4', 'L4'))
    rules.append(rule_template % ('L2', 'L2'))
    topology = '<topology name="%s">\n' % topology_name
    for topo in rules:
        topology = topology + '  ' + topo + '\n'
    topology = topology + '</topology>'
    topologies[topology_name] = topology


CWD = os.getcwd()
target_dir = os.path.join(CWD, "arch/top_arch_inst")
template_file_name = "top_arch_template.xml"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
else:
    for file in os.listdir(target_dir):
        os.remove(os.path.join(target_dir, file))
arch_target_dir = os.path.join(CWD, "arch/arch_inst")
if not os.path.exists(arch_target_dir):
    os.makedirs(arch_target_dir)
else:
    for file in os.listdir(arch_target_dir):
        os.remove(os.path.join(arch_target_dir, file))


def explore_local_routing(local_routing_params, global_routing_params):
    for local_param in local_routing_params:
        for topo_name, topology in global_routing_params.items():
            fo = open(os.path.join(os.path.dirname(target_dir), template_file_name), "rt")
            file_name = "G%d_I%d_F%d___%s_top_arch_inst.xml" % (local_param[0], local_param[1], local_param[2], topo_name)
            local_routing_inst = local_routing_template % local_param
            with open(os.path.join(target_dir, file_name), "wt") as fw:
                for line in fo:
                    line = re.sub(local_routing_pat, local_routing_inst, line)
                    line = re.sub(global_routing_pat, topology, line)
                    fw.write(line)
            fo.close()
    for file_inst in os.listdir(target_dir):
        file_inst_name = os.path.join(target_dir, file_inst)
        print("python3 -u generate_arch.py %s" % file_inst_name)
        os.system("python3 -u generate_arch.py %s" % file_inst_name)


explore_local_routing(local_routing_param_comb, topologies)

# generate vpr task config file
arch_target_dir = os.path.join(CWD, "arch/arch_inst")
arch_list_add = []
for file in os.listdir(arch_target_dir):
    added_str = "arch_list_add=%s" % file
    arch_list_add.append(added_str)
fo = open("./arch/config_template.txt", "rt")
with open("./arch/config.txt", "w") as fp:
    fp.writelines(fo.readlines())
    fp.write("\n".join(arch_list_add))
    fp.write(
        "\n\nscript_params=-starting_stage vpr --route_chan_width %d --timing_analysis off --max_router_iterations 25"
        % channel_width
    )
