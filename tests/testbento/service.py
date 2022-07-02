import bentoml
from bentoml.io import JSON, File, Multipart, NumpyNdarray, Text

svc = bentoml.Service("bentoctl-test-service")


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


@svc.api(input=JSON(), output=JSON())
def test_json1(input_json):
    return input_json
