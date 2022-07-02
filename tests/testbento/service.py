import bentoml
import numpy as np
from bentoml.io import JSON, File, Multipart, NumpyNdarray, Text

iris_clf_runner = bentoml.sklearn.get("iris_clf:latest").to_runner()

svc = bentoml.Service("bentoctl-test-service", runners=[iris_clf_runner])


@svc.api(input=JSON(), output=JSON())
def test_json(input_json):
    return input_json


@svc.api(input=File(), output=File())
def test_file(input_file):
    return input_file


input_spec = Multipart(arr=NumpyNdarray(), file=File())


@svc.api(input=input_spec, output=Text())
def test_multipart(arr, file):
    return ""


@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def sklearn_runner(input_series: np.ndarray) -> np.ndarray:
    return iris_clf_runner.run(input_series)
