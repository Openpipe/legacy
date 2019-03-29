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

        plt.bar(labels, values, align='center', alpha=0.5)

        output_filename = self.config['filename']
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im.save(output_filename)
        buf.close()
        im.close()
