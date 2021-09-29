import json
import logging
import os
import sys

from bentoml.saved_bundle import load_from_dir


api_name = os.environ["BENTOML_API_NAME"]
print('loading app: ', api_name)
print('Loading from dir...')
bento_service = load_from_dir('./')
print('bento service', bento_service)
bento_service_api = bento_service.get_inference_api(api_name)

this_module = sys.modules[__name__]


def api_func(event, context):
    if type(event) is dict and "headers" in event and "body" in event:
        prediction = bento_service_api.handle_aws_lambda_event(event)
        print(
            json.dumps(
                {
                    'event': event,
                    'prediction': prediction["body"],
                    'status_code': prediction["statusCode"],
                }
            )
        )

        if prediction["statusCode"] >= 400:
            logging.error('Error when predicting. Check logs for more information.')

        return prediction
    else:
        error_msg = (
            'Error: Unexpected Lambda event data received. Currently BentoML lambda '
            'deployment can only handle event triggered by HTTP request from '
            'Application Load Balancer.'
        )
        logging.error(error_msg)
        raise RuntimeError(error_msg)


setattr(this_module, api_name, api_func)
