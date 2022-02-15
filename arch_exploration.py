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
wires = [(1, 2), (2, 1), (4, 1), (6, 1)]
channel_width = sum(length * num * 2 * N for length, num in wires)
local_routing_param_comb = []
print(channel_width)
for lane_num in (1, 2, 3, 4, 6, 8):
    for I in range((N + 1) * K // 2, 81):
        if I % 2 == 1:
            continue
        if (K * N) % lane_num == 0 and I % lane_num == 0:
            for lim_size in range(
                max(channel_width // I, 4), 3 * channel_width // I + 1
            ):
                if lim_size % 2 == 1:
                    continue
                comb = (lane_num, I, lim_size)
                print(comb)
                local_routing_param_comb.append(comb)
print(len(local_routing_param_comb))

local_routing_pat = re.compile(r"%local_routing%")
local_routing_template = '<local_routing K="6" N="8" lane_num="%d" I="%d" O="16" fd="0.5" interlane_con_dir="1">\n\t<LIM mux_size="%d"/>\n\t<LEIM full_crossbar="1"/>\n</local_routing>'

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


def explore_local_routing(params):
    for param in params:
        fo = open(os.path.join(os.path.dirname(target_dir), template_file_name), "rt")
        file_name = "lane%d_I%d_limsize%d_top_arch_inst.xml" % param
        local_routing_inst = local_routing_template % param
        with open(os.path.join(target_dir, file_name), "wt") as fw:
            for line in fo:
                line = re.sub(local_routing_pat, local_routing_inst, line)
                fw.write(line)
        fo.close()
    for file_inst in os.listdir(target_dir):
        file_inst_name = os.path.join(target_dir, file_inst)
        print("python3 -u generate_arch.py %s" % file_inst_name)
        os.system("python3 -u generate_arch.py %s" % file_inst_name)


explore_local_routing(local_routing_param_comb)

# generate vpr task config file
arch_target_dir = os.path.join(CWD, "arch/arch_inst")
arch_list_add = []
for file in os.listdir(arch_target_dir):
    added_str = "arch_list_add=%s" % file
    arch_list_add.append(added_str)
fo = open("./arch/config_template.txt", "rt")
with open("config.txt", "wa") as fp:
    fp.writelines(fo.readlines())
    fp.write("\n".join(arch_list_add))
    fp.write(
        "\n\nscript_params=-starting_stage vpr --route_chan_width %d --timing_analysis off --max_router_iterations 25"
        % channel_width
    )
