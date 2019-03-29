from mdatapipe.core.pipeline import FilePipeline


def TestRun(filename):
    print("\nTesting", filename)
    test_fname = filename
    test_pipeline = FilePipeline(file=test_fname)
    test_pipeline.start()
    return test_pipeline.wait_end()
