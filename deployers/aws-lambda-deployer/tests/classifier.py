# iris_classifier.py
from bentoml import env, api, BentoService
from bentoml.adapters import DataframeInput, JsonInput, FileInput
from bentoml.types import JsonSerializable, FileLike


@env(infer_pip_packages=True)
class TestService(BentoService):

    @api(input=DataframeInput(), batch=True)
    def dfapi(self, df):
        print(df)
        return df

    @api(input=JsonInput(), batch=False)
    def jsonapi(self, json: JsonSerializable):
        print(json)
        return json

    @api(input=FileInput(), batch=False)
    def fileapi(self, file_stream: FileLike):
        print(file_stream)
        if file_stream.bytes_ is not None:
            return file_stream.bytes_
        else:
            return file_stream._stream.read()
