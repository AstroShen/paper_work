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
channel_width = sum(length*num*2*N for length, num in wires)
local_routing_param_comb = []
print(channel_width)
for lane_num in range(2, N+1):
    for I in range((N+1)*K//2 + 5, 81):
        if (K*N) % lane_num == 0 and I % lane_num == 0:
            for lim_size in range(max(channel_width//I, 4), 4*channel_width//I+1):
                if lim_size%2 == 1:
                    continue
                comb = (lane_num, I, lim_size)
                print(comb)
                local_routing_param_comb.append(comb)
print(len(local_routing_param_comb))

