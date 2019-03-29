from mdatapipe.core.pipeline import Pipeline


def TestRun(filename):
    print("\nTesting", filename)
    test_fname = filename
    test_pipeline = Pipeline(file=test_fname)
    test_pipeline.start(stop_on_error=True)
    result = test_pipeline.wait_end()
    if result is False:
        return None
    return True
