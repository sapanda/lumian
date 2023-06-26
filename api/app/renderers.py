from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            'data': {},
            'message': '',
        }
        # if direct message has been sent
        if isinstance(data, str):
            response_dict['message'] = data

        elif isinstance(data, dict):
            if data.get('data') or data.get('message'):
                if data.get('data'):
                    response_dict['data'] = data.get('data')
                if data.get('message'):
                    response_dict['message'] = data.get('message')
            else:
                # if direct data has been sent in dict format
                response_dict['data'] = data
        else:
            # if direct data has been sent in any other format
            response_dict['data'] = data
        data = response_dict
        return super().render(data, accepted_media_type, renderer_context)
