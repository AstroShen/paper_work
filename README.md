# 项目介绍
本项目以二级互连模式描述文件为输入，以VPR架构描述文件作为输出（钱嘉栋修改版本），用于探索二级互连架构。
# 文件结构介绍
1. setenv.py是一些环境设置，包括HSPICE路径等，移植到新环境时，路径修改修改;
2. tech.py和device_geometry.py是一些工艺设置，主要从Global is the new local: Fpga architecture at 5nm and beyond论文相关的开源项目得到，这部分属于todo，原本打算用产生的二级互连模式搭建网表方针的，我自己的做法是在上述论文项目上进行修改，就没有重写；
3. generate_arch.py是核心代码，用于产生二级互连模式;
4. arch_exploration.py是批量产生多种二级互连模式的代码，里面有自己设计的探索模式，可以依照自己的需求和想法更改;
5. arch文件夹下面包含产生二级互连模式描述文件和VPR架构描述文件的模板，程序输出结果也是在这个文件夹下，arch/top_arch_inst为生成的二级互连模式描述文件，arch/arch_inst为生成的VPR架构描述文件，arch/config.txt为跑VPR task所用的配置文件，具体参考VPR使用情况；
6. results文件夹下为我自己产生的一些数据，下面包含一些解析VPR输出文件的一些脚本，用于快速得到数据，属于文本数据处理工作;
7. 本目录下别的文件为tmp，可以忽略；
# 使用示例
使用generate_arch.py跑单个二级互连模式时，只需要指定二级互连模式描述文件。其可由arch/top_arch_template.xml产生。
python3 -u generate_arch.py top_arch_inst/xml/path
arch_exploration.py会利用top_arch_template.xml产生大量的top_arch_inst，再产生对应的arch_inst。
python3 -u arch_exploration.py
