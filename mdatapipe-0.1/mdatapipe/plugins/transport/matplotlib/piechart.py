from mdatapipe.core import PipelinePlugin
from PIL import Image
import io
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt  # NOQA: E402


"""
Requires: matplotlib Pillow
"""


class Plugin(PipelinePlugin):

    def on_input(self, item):

        labels = list(item.keys())
        values = list(item.values())

        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        output_filename = self.config['filename']
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im.save(output_filename)
        buf.close()
        im.close()
