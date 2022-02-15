#!/usr/bin/python3
import xml.etree.ElementTree as ET
import argparse
import networkx as nx
import re
import os
from itertools import chain
import pysnooper

# import matplotlib.pyplot as plt

K = 6
N = 10
Node = 7
Lane_num = 4
LIM_size = 4
I = 40
O = 10
Fd = 0.5
H_wires = []
V_wires = []
General_route_rule = []
SB_pattern = "wilton"
Lim_interlane_con_dir = 0
SB_interlane_con_dir = 1
Interlane_con_valid = True

parser = argparse.ArgumentParser()
parser.add_argument("arch", help="routing architecuture description")
args = parser.parse_args()
routing_arch = args.arch


def add_leim_node(G):
    ble_cnt = 0
    lane_cnt = 0
    lane_dist = [
        int(K * N / Lane_num)
        if i < Lane_num - int(K * N % Lane_num)
        else int(K * N / Lane_num) + 1
        for i in range(0, Lane_num)
    ]
    lane_deli = [0 if i == 0 else sum(lane_dist[0:i]) for i in range(0, len(lane_dist))]
    for i in range(0, K * N):
        ble_cnt = int(i / K)
        lut_input_cnt = int(i % K)
        lane_cnt = -1
        for j in lane_deli:
            if i >= j:
                lane_cnt += 1
        name = "lane_%d_ble_%d_%d" % (lane_cnt, ble_cnt, lut_input_cnt)
        G.add_node(
            name, node_type="leim", lane=lane_cnt, ble=ble_cnt, ble_i_cnt=lut_input_cnt
        )


def add_lim_node(G):
    lane_dist = [
        int(I / Lane_num) if i < Lane_num - int(I % Lane_num) else int(I / Lane_num) + 1
        for i in range(0, Lane_num)
    ]
    lane_deli = [0 if i == 0 else sum(lane_dist[0:i]) for i in range(0, len(lane_dist))]
    for i in range(I):
        lane_cnt = -1
        for j in lane_deli:
            if i >= j:
                lane_cnt += 1
        name = "lane_%d_I_%d" % (lane_cnt, i)
        G.add_node(name, node_type="lim", lane=lane_cnt, I=i)


def add_output_node(G):
    for i in range(O):
        ble_cnt = int(i / (O / N))
        ble_i_cnt = int(i % (O / N))
        name = "ble_%d_O_%d" % (ble_cnt, ble_i_cnt)
        G.add_node(name, node_type="output", ble=ble_cnt, ble_i_cnt=ble_i_cnt)


def add_channels_node(G):
    # add horizontal wires
    # FIXME: I assume H_wires and V_wires are identical, so renaming should be done!
    for h_wire in H_wires:
        wire_range = h_wire["range"]
        name = h_wire["name"]
        length = h_wire["length"]
        layer = h_wire["layer"]
        num_per_lut = h_wire["num_per_lut"]
        lane_dist = [
            int(num_per_lut * N * 4 / Lane_num)
            if i < Lane_num - int(num_per_lut * N * 4 % Lane_num)
            else num_per_lut * N * 4 // Lane_num + 1
            for i in range(Lane_num)
        ]
        lane_deli = [
            0 if i == 0 else sum(lane_dist[0:i]) for i in range(0, len(lane_dist))
        ]
        dir = {0: 0, 1: 0, 2: 0, 3: 0}  # 0->N, 1->E, 2->S, 3->W
        dir_lut = ("N", "E", "S", "W")
        for i in range(N * num_per_lut * 4):
            lane_cnt = -1
            for j in lane_deli:
                if i >= j:
                    lane_cnt += 1
            ble_cnt = int(i / (num_per_lut * 4))
            ble_i_cnt = int(i % num_per_lut)
            cur_dir = dir_lut[(i // num_per_lut) % 4]
            if cur_dir == "N" or cur_dir == "S":
                name = "lane_%d_ble_%d_V%d_%s_%d_end" % (
                    lane_cnt,
                    ble_cnt,
                    length,
                    cur_dir,
                    ble_i_cnt,
                )
                G.add_node(
                    name,
                    node_type="v_track",
                    length=length,
                    lane=lane_cnt,
                    ble=ble_cnt,
                    wire_cnt=ble_i_cnt,
                    direction=cur_dir,
                    layer=layer,
                    wire_range=wire_range,
                    begin=0,
                    num_per_lut=num_per_lut,
                )
                name = "lane_%d_ble_%d_V%d_%s_%d_beg" % (
                    lane_cnt,
                    ble_cnt,
                    length,
                    cur_dir,
                    ble_i_cnt,
                )
                G.add_node(
                    name,
                    node_type="v_track",
                    length=length,
                    lane=lane_cnt,
                    ble=ble_cnt,
                    wire_cnt=ble_i_cnt,
                    direction=cur_dir,
                    layer=layer,
                    wire_range=wire_range,
                    begin=1,
                    num_per_lut=num_per_lut,
                )
            else:
                name = "lane_%d_ble_%d_H%d_%s_%d_end" % (
                    lane_cnt,
                    ble_cnt,
                    length,
                    cur_dir,
                    ble_i_cnt,
                )
                G.add_node(
                    name,
                    node_type="h_track",
                    length=length,
                    lane=lane_cnt,
                    ble=ble_cnt,
                    wire_cnt=ble_i_cnt,
                    direction=cur_dir,
                    layer=layer,
                    wire_range=wire_range,
                    begin=0,
                    num_per_lut=num_per_lut,
                )
                name = "lane_%d_ble_%d_H%d_%s_%d_beg" % (
                    lane_cnt,
                    ble_cnt,
                    length,
                    cur_dir,
                    ble_i_cnt,
                )
                G.add_node(
                    name,
                    node_type="h_track",
                    length=length,
                    lane=lane_cnt,
                    ble=ble_cnt,
                    wire_cnt=ble_i_cnt,
                    direction=cur_dir,
                    layer=layer,
                    wire_range=wire_range,
                    begin=1,
                    num_per_lut=num_per_lut,
                )
    #
    #         name = 'lane_%d_ble_%d_H%d_W_%d_beg' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='h_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='W', layer=layer, wire_range=wire_range, begin=1, num_per_lut=num_per_lut)
    #         name = 'lane_%d_ble_%d_H%d_E_%d_end' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='h_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='E', layer=layer, wire_range=wire_range, begin=0, num_per_lut=num_per_lut)
    #         name = 'lane_%d_ble_%d_H%d_E_%d_beg' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='h_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='E', layer=layer, wire_range=wire_range, begin=1, num_per_lut=num_per_lut)
    # # add vertical wires
    # for v_wire in V_wires:
    #     wire_range = v_wire['range']
    #     name = v_wire['name']
    #     length = v_wire['length']
    #     layer = v_wire['layer']
    #     num_per_lut = v_wire['num_per_lut']
    #     lane_dist = [int(num_per_lut*N/Lane_num) if i < Lane_num-int(num_per_lut*N %
    #                                                                  Lane_num) else int(num_per_lut*N/Lane_num)+1 for i in range(0, Lane_num)]
    #     lane_deli = [0 if i == 0 else sum(lane_dist[0:i])
    #                  for i in range(0, len(lane_dist))]
    #     for i in range(N*num_per_lut):
    #         lane_cnt = -1
    #         for j in lane_deli:
    #             if i >= j:
    #                 lane_cnt += 1
    #         ble_cnt = int(i / num_per_lut)
    #         ble_i_cnt = int(i % num_per_lut)
    #         name = 'lane_%d_ble_%d_V%d_N_%d_end' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='v_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='N', layer=layer, wire_range=wire_range, begin=0, num_per_lut=num_per_lut)
    #         name = 'lane_%d_ble_%d_V%d_N_%d_beg' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='v_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='N', layer=layer, wire_range=wire_range, begin=1, num_per_lut=num_per_lut)
    #         name = 'lane_%d_ble_%d_V%d_S_%d_end' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='v_track', length=length, lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt,
    #                    direction='S', layer=layer, wire_range=wire_range, begin=0, num_per_lut=num_per_lut)
    #         name = 'lane_%d_ble_%d_V%d_S_%d_beg' % (
    #             lane_cnt, ble_cnt, length, ble_i_cnt)
    #         G.add_node(name, node_type='v_track', lane=lane_cnt, ble=ble_cnt, wire_cnt=ble_i_cnt, direction='S',
    #                    layer=layer, length=length, wire_range=wire_range, begin=1, num_per_lut=num_per_lut)


def add_lim2leim_edge(G):
    lim_nodes = {}
    for node in G.nodes(data=True):
        if node[1]["node_type"] == "lim":
            lane_cnt = node[1]["lane"]
            lim_nodes.setdefault(lane_cnt, []).append(node)
    for leim, attrs in G.nodes(data=True):
        if attrs["node_type"] != "leim":
            continue
        lane_cnt = attrs["lane"]
        for lim, attrs in lim_nodes[lane_cnt]:
            G.add_edge(lim, leim, mux_type="leim")


def add_feedback_edge(G):
    leim_nodes = {}
    for node in G.nodes(data=True):
        if node[1]["node_type"] == "leim":
            ble_cnt = node[1]["ble"]
            leim_nodes.setdefault(ble_cnt, []).append(node)
    out_fd_sinks_num = int(K * N * Fd)
    ble_cnt = 0
    ble_i_cnt = 0
    for out_node, attrs in G.nodes(data=True):
        if attrs["node_type"] != "output":
            continue
        for i in range(out_fd_sinks_num):
            if ble_cnt == N:
                ble_cnt = 0
                if ble_i_cnt == K - 1:
                    ble_i_cnt = 0
                else:
                    ble_i_cnt += 1
            leim_node = leim_nodes[ble_cnt][ble_i_cnt][0]
            G.add_edge(out_node, leim_node, mux_type="leim")
            ble_cnt += 1


def add_sb2lim_edge(G):
    input_pattern = list(filter(lambda x: x[-1] == "I", General_route_rule))
    h_wires_by_lane = {}
    v_wires_by_lane = {}
    for node in G.nodes(data=True):
        if node[1]["node_type"] in ("h_track", "v_track") and node[1]["begin"] == 0:
            lane_cnt = node[1]["lane"]
            if node[1]["wire_range"] in [source for source, _ in input_pattern]:
                if node[1]["node_type"] == "h_track":
                    h_wires_by_lane.setdefault(lane_cnt, []).append(node)
                else:
                    v_wires_by_lane.setdefault(lane_cnt, []).append(node)
    lim_by_lane = {}
    for node in G.nodes(data=True):
        if node[1]["node_type"] == "lim":
            lane_cnt = node[1]["lane"]
            lim_by_lane.setdefault(lane_cnt, []).append(node)
    dir_lut = ("N", "W", "S", "E")
    lim_cnt = 0
    # def get_wires_by_dir(wires, direction): return (
    #     wires for wire in wires if wire[-1]['direction'] == direction)
    for lane in range(Lane_num):
        lims_of_lane = lim_by_lane[lane]
        wires_of_lane = [] + h_wires_by_lane[lane] + v_wires_by_lane[lane]
        dir_wire_cursor_lut = {"N": 0, "W": 0, "E": 0, "S": 0}
        for lim, _ in lims_of_lane:
            dir_str = dir_lut[lim_cnt % 4]
            lim_cnt += 1
            wires_of_dir = []
            for wire in wires_of_lane:
                if wire[-1]["direction"] == dir_str:
                    wires_of_dir.append(wire)
            # for wire in wires_of_dir:
            #     print(wire)
            # sorted by `ble` and `wire_cnt`
            wires_of_dir = sorted(
                wires_of_dir, key=lambda wire: (wire[-1]["ble"], wire[-1]["wire_cnt"])
            )
            global LIM_size
            # When LIM_size < len(wires_of_lane), LIM will have multiple edges between LIM node and wire node.
            # if LIM_size > len(wires_of_dir):
            #     print('LIM_size: %d is bigger than number of MUXes(%d) inside the same lane! Make LIM_size = len(wires_of_dir)' % (
            #         LIM_size, len(wires_of_dir)))
            #     LIM_size = len(wires_of_dir)
            for i in range(LIM_size):
                dir_wire_cursor = dir_wire_cursor_lut[dir_str]
                G.add_edge(wires_of_dir[dir_wire_cursor][0], lim, mux_type="lim")
                if dir_wire_cursor == len(wires_of_dir) - 1:
                    dir_wire_cursor_lut[dir_str] = 0
                else:
                    dir_wire_cursor_lut[dir_str] += 1

            # # debug
            # for i in wires_of_dir:
            #     print(i[0])
            # print(len(wires_of_dir))
            # print(30*'-', '\n')
            # ########################
    # for src, sink, attrs in G.edges(data = True):
    #     if attrs['mux_type'] == 'lim':
    #         print((src, sink))
    # print(len(h_wires_by_lane[0]))
    # for i in h_wires_by_lane[0]:
    #     print(i[0])
    # for i in v_wires_by_lane[0]:
    #     print(i[0])
    # print('sum', sum(len(v_wires_by_lane[i]) for i in v_wires_by_lane))


def add_sb2sb_edge(G):
    wilton_offset_dict = {
        ("N", "W"): lambda t, w: (w - t) % w,
        ("N", "E"): lambda t, w: (t + 1) % w,
        ("N", "S"): lambda t, _: t % w,
        ("S", "W"): lambda t, w: (t + 1) % w,
        ("S", "E"): lambda t, w: (w - t - 2) % w,
        ("S", "N"): lambda t, _: t % w,
        ("E", "N"): lambda t, w: (w + t - 1) % w,
        ("E", "S"): lambda t, w: (w - t - 2) % w,
        ("E", "W"): lambda t, _: t % w,
        ("W", "N"): lambda t, w: (w - t) % w,
        ("W", "S"): lambda t, w: (w + t - 1) % w,
        ("W", "E"): lambda t, _: t % w,
    }
    universal_offset_dict = {
        ("N", "W"): lambda t, w: (w - t - 1) % w,
        ("N", "E"): lambda t, _: t % w,
        ("N", "S"): lambda t, _: t % w,
        ("S", "W"): lambda t, _: t % w,
        ("S", "E"): lambda t, w: (w - t - 1) % w,
        ("S", "N"): lambda t, _: t % w,
        ("E", "N"): lambda t, _: t % w,
        ("E", "S"): lambda t, w: (w - t - 1) % w,
        ("E", "W"): lambda t, _: t % w,
        ("W", "N"): lambda t, w: (w - t - 1) % w,
        ("W", "S"): lambda t, _: t % w,
        ("W", "E"): lambda t, _: t % w,
    }
    disjoint_offset_dict = {
        ("N", "W"): lambda t, _: t % w,
        ("N", "E"): lambda t, _: t % w,
        ("N", "S"): lambda t, _: t % w,
        ("S", "W"): lambda t, _: t % w,
        ("S", "E"): lambda t, _: t % w,
        ("S", "N"): lambda t, _: t % w,
        ("E", "N"): lambda t, _: t % w,
        ("E", "S"): lambda t, _: t % w,
        ("E", "W"): lambda t, _: t % w,
        ("W", "N"): lambda t, _: t % w,
        ("W", "S"): lambda t, _: t % w,
        ("W", "E"): lambda t, _: t % w,
    }
    sb_rules = [
        pat
        for pat in General_route_rule
        if pat[0].endswith("range") and pat[1].endswith("range")
    ]
    wires_by_lane = {}
    for node in G.nodes(data=True):
        if node[-1]["node_type"] in ("h_track", "v_track"):
            wires_by_lane.setdefault(node[-1]["lane"], []).append(node)

    def get_wires_by_dir(wires, direction):
        return [
            wires[i]
            for i in range(len(wires))
            if wires[i][-1]["direction"] == direction
        ]

    def get_wires_by_beg(wires, begin):
        return [wires[i] for i in range(len(wires)) if wires[i][-1]["begin"] == begin]

    def get_wires_by_range(wires, wire_range):
        return [
            wires[i]
            for i in range(len(wires))
            if wires[i][-1]["wire_range"] == wire_range
        ]

    def get_wires_by_len(wires, length):
        return [wires[i] for i in range(len(wires)) if wires[i][-1]["length"] == length]

    for lane in range(Lane_num):
        wires_of_lane = wires_by_lane[lane]
        for turn in wilton_offset_dict:
            src_dir = turn[0]
            sink_dir = turn[1]
            if SB_pattern == "wilton":
                offset_formula = wilton_offset_dict[turn]
            elif SB_pattern == "universal":
                offset_formula = universal_offset_dict[turn]
            else:
                assert SB_pattern == "disjoint"
                offset_formula = disjoint_offset_dict[turn]
            for sb_rule in sb_rules:
                src_range = sb_rule[0]
                sink_range = sb_rule[1]
                # sb pattern between wires of same length should be (wilton, disjoint, universal)
                src_wires_len_of_range = tuple(
                    set(
                        [
                            wire["length"]
                            for wire in H_wires + V_wires
                            if wire["range"] == src_range
                        ]
                    )
                )
                sink_wires_len_of_range = tuple(
                    set(
                        [
                            wire["length"]
                            for wire in H_wires + V_wires
                            if wire["range"] == sink_range
                        ]
                    )
                )
                for wire_len in src_wires_len_of_range:
                    exact_drive_combs = tuple(
                        [(wire_len, x) for x in sink_wires_len_of_range]
                    )
                    for drive_comb in exact_drive_combs:
                        src_len = drive_comb[0]
                        sink_len = drive_comb[1]
                        src_wires = get_wires_by_beg(
                            get_wires_by_len(
                                get_wires_by_dir(wires_of_lane, src_dir), src_len
                            ),
                            0,
                        )
                        sink_wires = get_wires_by_beg(
                            get_wires_by_len(
                                get_wires_by_dir(wires_of_lane, sink_dir), sink_len
                            ),
                            1,
                        )
                        src_wires = sorted(
                            src_wires,
                            key=lambda wire: (wire[1]["ble"], wire[1]["wire_cnt"]),
                        )
                        sink_wires = sorted(
                            sink_wires,
                            key=lambda wire: (wire[1]["ble"], wire[1]["wire_cnt"]),
                        )
                        # print('drive_comb: %s' % str(drive_comb))
                        # for i in src_wires:
                        #     print(i[0])
                        # for i in sink_wires:
                        #     print(i[0])
                        num_src_wires = len(src_wires)
                        num_sink_wires = len(sink_wires)
                        w = min(num_src_wires, num_sink_wires)
                        # TODO: when num_src_wires is great than num_sink_wires, there are two ways to assign src_wires to sink_wires, for now i am abeying to the rule that every src_wire will connect to a sink_wire
                        for index, src_wire in enumerate(src_wires):
                            # # uncomment the following `if` when every src_wire will connect to a sink_wire
                            if index == num_sink_wires:
                                break
                            t = index
                            sink_t = offset_formula(t, w)
                            try:
                                assert sink_t >= 0 and sink_t < num_sink_wires
                            except:
                                print(
                                    "sink_t: %s" % sink_t,
                                    "num_sink_wires: %s" % num_sink_wires,
                                    "src_t: %s" % t,
                                    "num_src_wires: %s" % num_src_wires,
                                )
                            sink_wire = sink_wires[sink_t]
                            # print(10*'-', sink_wire[0])
                            G.add_edge(
                                src_wire[0],
                                sink_wire[0],
                                mux_type="L%d" % sink_wire[1]["length"],
                            )
    if Interlane_con_valid:
        wires_by_ble = {}
        for node in G.nodes(data=True):
            if node[-1]["node_type"] in ("h_track", "v_track"):
                wires_by_ble.setdefault(node[-1]["ble"], []).append(node)
        driving_ble_map = {
            0: [],
            1: [0],
            2: [0],
            3: [1],
            4: [2],
            5: [3],
            6: [4],
            7: [5, 6],
        }
        if SB_interlane_con_dir == 1:
            # driving_ble_map = {0: [1, 2], 1: [3], 2: [
            #     4], 3: [5], 4: [6], 5: [7], 6: [7], 7: []}
            driving_ble_map = {
                0: [1, 2],
                1: [3, 0],
                2: [2, 4],
                3: [1, 5],
                4: [2, 6],
                5: [3, 7],
                6: [4, 7],
                7: [5, 6],
            }
        for ble in range(N):
            driving_bles = driving_ble_map[ble]
            if not driving_bles:
                continue
            wires_of_ble = get_wires_by_beg(wires_by_ble[ble], 1)
            wires_of_driving_ble = []
            for driving_ble in driving_bles:
                wires_of_driving_ble = wires_of_driving_ble + get_wires_by_beg(
                    wires_by_ble[driving_ble], 1
                )
            for wire, attrs in wires_of_ble:
                node_type = attrs["node_type"]
                length = attrs["length"]
                direction = attrs["direction"]
                wire_cnt = attrs["wire_cnt"]
                driving_wires = list(
                    filter(
                        lambda x: x[1]["node_type"] == node_type
                        and x[1]["length"] == length
                        and x[1]["direction"] == direction
                        and x[1]["wire_cnt"] == wire_cnt,
                        wires_of_driving_ble,
                    )
                )
                for driving_wire in driving_wires:
                    G.add_edge(driving_wire[0], wire, mux_type="L%d_medium" % length)


def add_out2sb_edge(G):
    out_rules = [pat for pat in General_route_rule if pat[0] == "O"]
    output_nodes = [
        node for node in G.nodes(data=True) if node[1]["node_type"] == "output"
    ]

    def get_output_by_ble(ble):
        return [node for node in output_nodes if node[1]["ble"] == ble]

    wire_beg_nodes = [
        node
        for node in G.nodes(data=True)
        if node[1]["node_type"] in ("h_track", "v_track") and node[1]["begin"] == 1
    ]
    # # TODO: the following commented for-range is alternative method to assign each output pin to each wire of different type
    # # the key is (ble, direction, length)
    # keys_of_wire_type = []
    # wires_of_unique_type = []
    # for node, attrs in wire_beg_nodes:
    #     key = (attrs['ble'], attrs['direction'], attrs['length'])
    #     if key not in keys_of_wire_type:
    #         keys_of_wire_type.append(key)
    #         wires_of_unique_type.append((node, attrs))
    # for node, attrs in wires_of_unique_type:
    #     ble = attrs['ble']
    #     ble_outputs = get_output_by_ble(ble)
    #     for ble_out in ble_outputs:
    #         G.add_edge(ble_out[0], node, mux_type='L%d'%attrs['length'])
    for node, attrs in wire_beg_nodes:
        if attrs["wire_range"] in [range for _, range in out_rules]:
            ble = attrs["ble"]
            ble_outputs = get_output_by_ble(ble)
            for ble_out in ble_outputs:
                G.add_edge(ble_out[0], node, mux_type="L%d" % attrs["length"])


def generate_detailed_routing():
    G = nx.DiGraph()
    add_leim_node(G)
    add_lim_node(G)
    add_output_node(G)
    add_channels_node(G)
    add_lim2leim_edge(G)
    add_feedback_edge(G)
    add_sb2lim_edge(G)
    add_sb2sb_edge(G)
    add_out2sb_edge(G)
    view_graph(G)
    return G


def view_graph(G):
    print(G.number_of_edges())


def generate_arch_file(G):
    """This function generates a revised version of VPR arch file supported by QianJiaDong"""
    ble_pin_name_lut = {
        0: "Ia",
        1: "Ib",
        2: "Ic",
        3: "Id",
        4: "Ie",
        5: "If",
        6: "Ig",
        7: "Ih",
        8: "Ii",
        9: "Ij",
    }
    # generate switch list
    switch_sizes = {}
    for node, attrs in G.nodes(data=True):
        node_type = attrs["node_type"]
        if node_type in ("h_track", "v_track"):
            node_type = "l%d" % attrs["length"]
        if G.in_degree(node):
            switch_sizes.setdefault(node_type, set()).add(G.in_degree(node))
        # if attrs['node_type'] == 'leim':
        #     print(10*'-',node,': ',G.in_degree(node))
        #     # predecessors = G.successors(node)
        #     predecessors = G.predecessors(node)
        #     for pre_node in predecessors:
        #         print(pre_node)
    switch_template = '<switch Cin="0.000000e+00" Cout="0.000000e+00" R="0.000000" Tdel="%e" buf_size="%f" mux_trans_size="%f" name="%s" type="mux">\n'
    multi_switch_template = '<switch Cin="0.000000e+00" Cout="0.000000e+00" R="0.000000" buf_size="%f" mux_trans_size="%f" name="%s" type="mux">\n'
    specific_size = '\t<Tdel delay="%e" num_inputs="%d"/>\n'
    switch_inst_list = []
    for node_type, sizes in switch_sizes.items():
        switch_inst = ""
        if len(sizes) == 1:
            switch_inst = switch_template.replace(">\n", "/>") % (
                5.772e-10,
                28.3655846906,
                1.25595750289,
                node_type,
            )
        elif len(sizes) > 1:
            switch_inst = multi_switch_template % (
                28.3655846906,
                1.25595750289,
                node_type,
            )
            for size in sizes:
                switch_inst += specific_size % (5.772e-10, size)
            switch_inst += "</switch>"
        else:
            exit(-1)
        switch_inst_list.append(switch_inst)
    # for i in switch_inst_list:
    #     print(i)

    # generate segment list
    segment_template = '<segment Cmetal="0.000000e+00" Rmetal="0.000000" freq="%f" length="%d" name="%s" type="unidir">\n\t<mux name="%s"/>\n\t<sb type="pattern">%s</sb>\n\t<cb type="pattern">%s</cb>\n</segment>'
    segment_inst_list = []
    # TODO: for now, vertical and horizontal channels are identical, the following for-range need to be modified when they are different
    for wire in H_wires:
        name = wire["name"]
        length = int(name[1:])
        sb_pattern = "1 " + (length - 1) * "0 " + "1"
        cb_pattern = "1" + max(length - 2, 0) * " 0" + (" 1" if length != 1 else "")
        freq = float(wire["num_per_lut"] * wire["length"])
        segment_inst = segment_template % (
            freq,
            length,
            name,
            name.lower(),
            sb_pattern,
            cb_pattern,
        )
        segment_inst_list.append(segment_inst)
    # for seg in segment_inst_list:
    #     print(seg)

    # generate mux
    reverse_dir = {"N": "S", "S": "N", "W": "E", "E": "W"}
    mux_detail_template = (
        '\t<from from_detail="%s" name="%s" switchpoint="0" type="%s"/>\n'
    )
    mux_template = '\t<from mux_name="%s"/>\n'
    lim_inst_list = {}
    leim_inst_list = {}
    driver_mux_inst_list = {}
    first_stage_driver_mux_inst_list = {}
    for node, attrs in G.nodes(data=True):
        node_type = attrs["node_type"]
        mux_size = G.in_degree(node)
        if mux_size == 0:
            continue
        mux_inst = ""
        if node_type == "lim":
            mux_name = "%s-%d" % (node_type, attrs["I"])
            mux_inst = '<mux name="%s">\n' % mux_name
            for src_node in G.predecessors(node):
                src_attrs = G.nodes[src_node]
                if src_attrs["node_type"] in ("h_track", "v_track"):
                    assert src_attrs["begin"] == 0
                    mux_inst += mux_detail_template % (
                        "%s%d"
                        % (
                            reverse_dir[src_attrs["direction"]],
                            src_attrs["ble"] * src_attrs["num_per_lut"]
                            + src_attrs["wire_cnt"],
                        ),
                        "L%d" % src_attrs["length"],
                        "seg",
                    )
                elif src_attrs["node_type"] == "output":
                    # TODO: i assume the output can have at most 2 outputs (o, q) per ble
                    mux_inst += mux_detail_template % (
                        "%s:%d"
                        % (
                            "o" if src_attrs["ble_i_cnt"] == 0 else "q",
                            src_attrs["ble"],
                        ),
                        "plb",
                        "pb",
                    )
                else:
                    # TODO: lim mux may have sources from other lims of leims, it depends later.
                    exit(-1)
            mux_inst += "</mux>"
            lim_inst_list[mux_name] = mux_inst
        elif node_type == "leim":
            mux_name = "%s-%d" % (node_type, attrs["ble"] * K + attrs["ble_i_cnt"])
            to_pin = "I%s:%d" % (chr(attrs["ble"] + 97), attrs["ble_i_cnt"])
            mux_inst = '<mux name="%s" to_pin="%s">\n' % (mux_name, to_pin)
            from_mux = ""
            for src_node in G.predecessors(node):
                src_attrs = G.nodes[src_node]
                if src_attrs["node_type"] == "lim":
                    from_mux += "%s-%d " % (src_attrs["node_type"], src_attrs["I"])
                elif src_attrs["node_type"] == "output":
                    # TODO: i assume the output can have at most 2 outputs (o, q) per ble
                    mux_inst += mux_detail_template % (
                        "%s:%d"
                        % (
                            "o" if src_attrs["ble_i_cnt"] == 0 else "q",
                            src_attrs["ble"],
                        ),
                        "plb",
                        "pb",
                    )
                else:
                    # TODO: i assume the leim can have sources from lim and output, it depends later.
                    exit(-1)
            mux_inst = mux_inst + mux_template % from_mux.rstrip() + "</mux>"
            leim_inst_list[mux_name] = mux_inst
        elif node_type in ("h_track", "v_track"):
            mux_name = "%s-L%d-%d" % (
                attrs["direction"],
                attrs["length"],
                attrs["ble"] * attrs["num_per_lut"] + attrs["wire_cnt"],
            )
            mux_inst = '<mux name="%s" to_seg_name="%s" to_track="%s">\n' % (
                mux_name,
                "L%d" % attrs["length"],
                "%s%d"
                % (
                    attrs["direction"],
                    attrs["ble"] * attrs["num_per_lut"] + attrs["wire_cnt"],
                ),
            )
            from_first_stage_mux = []
            for src_node in G.predecessors(node):
                src_attrs = G.nodes[src_node]
                if src_attrs["node_type"] in ("h_track", "v_track"):
                    if src_attrs["begin"] == 1:
                        from_first_stage_mux.append(
                            "%s_ble_%d_L%d_%d"
                            % (
                                src_attrs["direction"],
                                src_attrs["ble"],
                                src_attrs["length"],
                                src_attrs["ble"] * src_attrs["num_per_lut"]
                                + src_attrs["wire_cnt"],
                            )
                        )
                    else:
                        mux_inst += mux_detail_template % (
                            "%s%d"
                            % (
                                reverse_dir[src_attrs["direction"]],
                                src_attrs["ble"] * src_attrs["num_per_lut"]
                                + src_attrs["wire_cnt"],
                            ),
                            "L%d" % src_attrs["length"],
                            "seg",
                        )
                elif src_attrs["node_type"] == "output":
                    # TODO: i assume the output can have at most 2 outputs (o, q) per ble
                    mux_inst += mux_detail_template % (
                        "%s:%d"
                        % (
                            "o" if src_attrs["ble_i_cnt"] == 0 else "q",
                            src_attrs["ble"],
                        ),
                        "plb",
                        "pb",
                    )
                else:
                    # TODO: lim mux may have sources from other lims of leims, it depends later.
                    exit(-1)
            mux_inst += '\t<from mux_name="%s"/>\n' % " ".join(from_first_stage_mux)
            mux_inst += "</mux>"

            # add first stage mux
            driver_mux_inst_list[mux_name] = mux_inst
            for first_stage_mux in from_first_stage_mux:
                if first_stage_mux not in first_stage_driver_mux_inst_list:
                    from_detail = (
                        first_stage_mux.split("_")[0] + first_stage_mux.split("_")[-1]
                    )
                    wire_name = first_stage_mux.split("_")[3]
                    first_stage_mux_inst = (
                        '<mux name="%s">\n\t<from from_detail="%s" name="%s" switchpoint="0" type="seg"/>\n</mux>'
                        % (first_stage_mux, from_detail, wire_name)
                    )
                    first_stage_driver_mux_inst_list[
                        first_stage_mux
                    ] = first_stage_mux_inst
        else:
            exit(-1)

    # segment group
    seg_group_template = '<seg_group name="%s" track_nums="%d">\n\t<from name="L1" num_foreach="1" total_froms="8" type="seg"/>\n</seg_group>'
    seg_group_inst_list = []
    for wire in H_wires:
        seg_group_inst = seg_group_template % (
            "L%d" % wire["length"],
            N * wire["num_per_lut"],
        )
        seg_group_inst_list.append(seg_group_inst)

    # write template file
    switch_inst_str = "\n".join(switch_inst_list)
    segment_inst_str = "\n".join(segment_inst_list)
    lim_inst_str = "\n".join(lim_inst_list.values())
    leim_inst_str = "\n".join(leim_inst_list.values())
    driver_mux_inst_str = "\n".join(driver_mux_inst_list.values())
    first_stage_driver_mux_inst_str = "\n".join(
        first_stage_driver_mux_inst_list.values()
    )
    seg_group_inst_str = "\n".join(seg_group_inst_list)
    gsb_seg_group_str = (
        '<gsb gsb_seg_group="%d" name="gsb" pbtype_name="plb memory io mult_36">\n'
        % len(H_wires)
    )
    switch_pat = re.compile(r"%switch%")
    segment_pat = re.compile(r"%segment%")
    lim_pat = re.compile(r"%lim_mux%")
    leim_pat = re.compile(r"%leim_mux%")
    driver_mux_pat = re.compile(r"%driver_mux%")
    first_stage_driver_mux_pat = re.compile(r"%first_stage_driver_mux%")
    seg_group_pat = re.compile(r"%seg_group%")
    gsb_seg_group_pat = re.compile(r"gsb_seg_group")

    CWD = os.getcwd()
    target_dir = os.path.join(CWD, "arch/arch_inst")
    template_file_name = "arch_file_template.xml"
    arch_file_template = open(
        os.path.join(os.path.dirname(target_dir), template_file_name), "rt"
    )
    arch_file_inst = os.path.basename(routing_arch)
    with open(os.path.join(target_dir, arch_file_inst), "wt") as fp:
        for line in arch_file_template:
            line = re.sub(switch_pat, switch_inst_str, line)
            line = re.sub(segment_pat, segment_inst_str, line)
            line = re.sub(lim_pat, lim_inst_str, line)
            line = re.sub(leim_pat, leim_inst_str, line)
            line = re.sub(driver_mux_pat, driver_mux_inst_str, line)
            line = re.sub(
                first_stage_driver_mux_pat, first_stage_driver_mux_inst_str, line
            )
            line = re.sub(seg_group_pat, seg_group_inst_str, line)
            if gsb_seg_group_pat.search(line):
                line = gsb_seg_group_str
            fp.write(line)
    arch_file_template.close()

    # template_file = "./arch_file.template"
    # with open(template_file, 'w') as fp:
    #     fp.write(re.sub(r'%switchlist%', switchlist_template, fp.read()))


def arch_parser(routing_arch):
    global K
    global N
    global Node
    global Lane_num
    global LIM_size
    global I
    global O
    global Fd
    global H_wires
    global V_wires
    global General_route_rule
    tree = ET.parse(routing_arch)
    root = tree.getroot()
    local_routing = root.find("local_routing")
    general_routing = root.find("general_routing")
    # local routing parse
    assert local_routing is not None
    K = int(local_routing.attrib["K"])
    N = int(local_routing.attrib["N"])
    Lane_num = int(local_routing.attrib["lane_num"])
    if Lane_num == 1:
        Interlane_con_valid = False
    I = int(local_routing.attrib["I"])
    O = int(local_routing.attrib["O"])
    Fd = float(local_routing.attrib["fd"])
    Lim_interlane_con_dir = int(local_routing.attrib["interlane_con_dir"])
    lim = local_routing.find("LIM")
    assert lim is not None
    lim_mux_size = int(lim.attrib["mux_size"])
    assert (K * N) % Lane_num == 0
    LIM_size = lim_mux_size
    # general_routing parse
    assert general_routing is not None
    SB_pattern = general_routing.attrib["pattern"]
    SB_interlane_con_dir = int(general_routing.attrib["interlane_con_dir"])
    horizontal = general_routing.find("horizontal")
    vertical = general_routing.find("vertical")
    assert horizontal is not None
    assert vertical is not None
    for child in horizontal:
        h_wire = {}
        h_wire["range"] = child.tag
        h_wire.update(child.attrib)
        h_wire["length"] = int(h_wire["length"])
        h_wire["num_per_lut"] = int(h_wire["num_per_lut"])
        H_wires.append(h_wire)
    for child in vertical:
        v_wire = {}
        v_wire["range"] = child.tag
        v_wire.update(child.attrib)
        v_wire["length"] = int(v_wire["length"])
        v_wire["num_per_lut"] = int(v_wire["num_per_lut"])
        V_wires.append(v_wire)
    topology = general_routing.find("topology")
    assert topology is not None
    for child in topology:
        source = child.attrib["source"]
        sink = child.attrib["sink"]
        General_route_rule.append((source, sink))


if __name__ == "__main__":
    arch_parser(routing_arch)
    G = generate_detailed_routing()
    generate_arch_file(G)
    print(
        "channel_width: ",
        2 * N * sum(wire["length"] * wire["num_per_lut"] for wire in H_wires),
    )
    # print(H_wires)
    # print(V_wires)
    # print(General_route_rule)
    # print(K, N, I, O, LIM_range, Fd)
