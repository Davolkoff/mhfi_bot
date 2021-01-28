import numpy as np  # библиотека для математических операций, выступает дополнением для matplotlit
import matplotlib.pyplot as plt  # библиотека для создания графиков
import io  # библиотека для работы с оперативной памятью


# создание пончикового графика
def pie(data, directions, name):
    with io.BytesIO() as buf:
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
            ax.annotate(directions[i], xy=(x, y), xytext=(1.2 * np.sign(x), 1.3 * y), horizontalalignment=halignment,
                        **kw)

        ax.set_title(name, x=1.3, y=1)  # название графика
        plt.savefig(buf, format='jpg')
        buf.seek(1)
        return io.BytesIO(buf.getvalue())



