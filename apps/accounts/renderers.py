# from rest_framework.renderers import JSONRenderer

# class CustomJSONRenderer(JSONRenderer):
#     def render(self, data, accepted_media_type=None, renderer_context=None):
#         print(data)
#         if 'error' in data:
#             getattr(
#                 renderer_context.get('view').get_serializer().Meta,
#                 'resource_name', 'objects')
#             # call super to render the response
#             response = super(CustomJSONRenderer,
#                              self).render(data, accepted_media_type,
#                                           renderer_context)
#             print(response)

#             return response

#         else:
#             response_data = {
#                 'success': {
#                     'message': '',
#                     'data': data,
#                     'status_code': 'success'
#                 }
#             }

#             getattr(
#                 renderer_context.get('view').get_serializer().Meta,
#                 'resource_name', 'objects')
#             # call super to render the response
#             response = super(CustomJSONRenderer,
#                              self).render(response_data, accepted_media_type,
#                                           renderer_context)

#             return response
