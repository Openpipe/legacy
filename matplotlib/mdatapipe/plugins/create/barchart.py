from mdatapipe.engine import PluginRuntime
from PIL import Image
import io
import matplotlib
import numpy as np

matplotlib.use('Agg')
from matplotlib import pyplot as plt  # NOQA: E402


"""
Requires: matplotlib numpy Pillow
"""


class Plugin(PluginRuntime):

    def on_start(self, config):
        self.labels = []
        self.values = []

    def on_input(self, item):

        labels_key = self.config['labels_key']
        values_key = self.config['values_key']
        self.labels.append(item[labels_key])
        self.values.append(item[values_key])

    def on_complete(self):
        fig1, ax1 = plt.subplots()
        y_pos = np.arange(len(self.labels))
        rects = ax1.bar(y_pos, self.values, align='center')
        plt.ylabel(self.config['ylabel'])
        for i, rect in enumerate(rects):
            xloc = rect.get_x() + rect.get_width()/2.0
            yloc = rect.get_y() + 3
            ax1.text(
                xloc, yloc, self.labels[i], rotation=90, verticalalignment='bottom', size='smaller',
                horizontalalignment='center',
                )
        ax1.get_xaxis().set_visible(False)
        output_filename = self.config['path']
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=400)
        buf.seek(0)
        im = Image.open(buf)
        im.save(output_filename)
        buf.close()
        im.close()
