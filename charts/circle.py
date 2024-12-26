import matplotlib
from typing import List, Tuple

# matplotlib.use('Agg')  # 使用Agg后端，这个后端适用于生成图像文件但不显示它们
matplotlib.use('TkAgg')  # 选择合适的后端，如Agg, TkAgg
import matplotlib.pyplot as plt
import numpy as np
import random as rm

# plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
# plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

# 设置默认字体为'Arial'
matplotlib.rcParams['font.family'] = 'Arial'
# matplotlib.rcParams['font.family'] = 'Times New Roman'


# 返回一个 rgba 颜色，透明度在 (10, 100) 范围内
def generate_rgba_color(a: int = 10, b: int = 100):
    return '#' + ''.join(rm.choice('0123456789ABCDEF') for _ in range(6)) + str(rm.uniform(a, b))


def bi_layered_circular_diagram(values: List[Tuple], labels_1: List, labels_2: List):
    """
    双层环形图
    :param values: 按组划分的数值，全部展开后为外层环的数值，按组求和后为内层环的数值
    :param labels_1: 内层环的标签
    :param labels_2: 外层环的标签
    :return:
    """
    
    # 设置数据值
    values_1 = [sum(v) for v in values]
    # values_2 = [*values[0], *values[1], *values[2]]
    values_2 = [i for v in values for i in v]
    print(values_1)
    print(values_2)
    # values_1 = [48.0, 31.0, 21.0]
    # values_2 = [12.5, 10.0, 12.5, None, 18.0, 13.0, None]

    # 设置扇区颜色
    colors_1 = [generate_rgba_color for _ in range(len(values_1))]
    # RGBA 颜色，最后两位表示透明度
    colors_2 = [generate_rgba_color for _ in range(len(values_2))]

    # 设置阴影颜色
    explode_1 = tuple(0 for _ in range(len(values_1)))
    explode_2 = tuple(0 for _ in range(len(values_2)))

    r1, r2 = 1.0, 1.35

    # 绘制双层饼图的时候得先绘制大图，在绘制小图
    # 外层圆环
    plt.pie(
        values_2,
        labels=labels_2,
        colors=colors_2,
        radius=r2,
        explode=explode_2,
        autopct='%1.1f%%',  # 在扇形中显示百分比
        pctdistance=0.87,
        startangle=60,
        wedgeprops=dict(width=1.0, edgecolor='w'),
    )
    # 内层饼图
    plt.pie(
        values_1,
        labels=labels_1,
        colors=colors_1,
        radius=r1,
        explode=explode_1,
        # autopct='%1.1f%%',  # 在扇形中显示百分比
        # pctdistance=1.0,  # 百分比标签距圆心距离
        labeldistance=0.25,  # 标签距圆心距离
        startangle=60,
        textprops={'fontname': 'Arial', 'fontsize': 12},
        wedgeprops=dict(width=1.0, edgecolor='w')
    )
    # plt.title('Bi Layered Circular Diagram')

    # 显示图形
    plt.show()


if __name__ == '__main__':
    # 设置最小分度值
    V = 1 / 13
    bi_layered_circular_paradigm(
        values=[(2 * V, 2 * V, 2 * V, 3 * V), (V, V), (V, V)],
        labels_1=['Chatting', 'Emotional', 'Feedback'],
        labels_2=['Consistency', 'Coherence', 'Expressive', 'Safety', 'Empathy', 'Helpful', 'Favourite', 'Character']
    )
