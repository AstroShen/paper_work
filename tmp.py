import xml.etree.ElementTree as ET
# with open('./arch_file.xml', 'wt') as fp:
mux_template = '<mux name="%s">\n\t<from from_detail="%s" name="L1" switchpoint="0" type="seg"/>\n</mux>\n'
num_per_lut = 10
num_ble = 8
num_lane = 4
num_wires_per_lane = num_per_lut*num_ble//num_lane
dir_list = ('N', 'S', 'W', 'E')
first_stage = {}
for dir in dir_list:
    for lane in range(0, num_lane):
        for index in range(num_wires_per_lane):
            mux_name = '%s_lane_%d_%d' % (dir, lane, lane*num_wires_per_lane + index)
            from_detail = '%s%d' % (dir, lane*num_wires_per_lane + index)
            mux_inst = mux_template % (mux_name, from_detail)
            first_stage[mux_name] = mux_inst
first_stage_str = ''
for _, mux_inst in first_stage.items():
    first_stage_str = first_stage_str + mux_inst

root = ET.parse('./arch/paper_work/arch_file.xml').getroot()
for mux in root.findall('./gsb_arch/gsb/multistage_muxs/second_stage/mux'):
    # print(mux.attrib['name'], mux.attrib['to_track'])
    go_dir = mux.attrib['to_track'][0]
    wire_index = int(mux.attrib['to_track'][1:])
    lane = wire_index // (num_per_lut*num_ble//num_lane)
    from_index = (wire_index- num_wires_per_lane) % (num_per_lut*num_ble)
    from_lane =  (lane-1)%num_lane
    from_wire_name = '%s_lane_%d_%d' % (go_dir, from_lane, from_index)
    attr = {'mux_name': from_wire_name}
    ET.SubElement(mux, 'from', attr)
    # ET.dump(mux)
print(ET.tostring(root))
with open('./arch/paper_work/arch_file_patched.xml', 'wb') as fp:
    fp.write(ET.tostring(root))
    fp.write(str.encode(first_stage_str))
