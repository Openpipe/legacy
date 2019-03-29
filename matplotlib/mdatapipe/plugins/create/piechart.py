from mdatapipe.engine import PluginRuntime
from PIL import Image
import io
import matplotlib


matplotlib.use('Agg')
from matplotlib import pyplot as plt  # NOQA: E402


"""
Requires: matplotlib Pillow
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
        ax1.pie(self.values, labels=self.labels, autopct='%1.1f%%', shadow=True, startangle=90)

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        output_filename = self.config['path']
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im.save(output_filename)
        buf.close()
        im.close()
