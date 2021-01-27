import numpy as np  # библиотека для математических операций, выступает дополнением для matplotlit
import matplotlib.pyplot as plt  # библиотека для создания графиков


# создание пончикового графика
async def pie(data, directions, name):
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        halignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(directions[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y), horizontalalignment=halignment, **kw)

    ax.set_title("Куда я вложился")  # название графика

    plt.savefig(str(name) + '_pie')  # сохранение графика в png
