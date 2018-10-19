import logging

from django.utils.deprecation import MiddlewareMixin

LOG = logging.getLogger('kinesis_middleware')


class KinesisMiddleware(MiddlewareMixin):
    """
    Middleware that intercepts requests and sends request data related to certain methods/models
    to AWS Kinesis stream.
    """

    def __init__(self, get_response):
        super().__init__()
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # TODO: move these constants to app settings
        METHODS_OF_INTEREST = (
            'GET',  # for testing only, don't need to actually ship this to analytics
            # 'PATCH',
            'POST',
            # 'PUT',
        )
        MODELS_OF_INTEREST = (
            'Cart',
            'Product',
            'User',
        )

        # Determine method and if it's valid.
        if request.method not in METHODS_OF_INTEREST:
            return response

        # Determine model based on request/view info and if it's valid.
        view_func = request.resolver_match.func
        view = view_func.cls
        modelview_or_queryset = getattr(view, 'queryset', view)
        model_name = modelview_or_queryset.model._meta.object_name if modelview_or_queryset else \
            None
        if model_name not in MODELS_OF_INTEREST:
            return response

        # Build Record to push to Kinesis
        record = {
            'method': request.method,
            'action': view_func.actions.get(request.method.lower()),
            'entity': model_name,
            'query': request.GET,
        }
        if request.POST:
            record['data'] = request.POST
        if request.FILES:
            record['files'] = request.FILES.keys()

        # Write Request Record to Kinesis
        try:
            # TODO: Place Kinesis client writer here.
            pass
        except Exception:
            # We don't want something wrong with Kinesis to blow up all requests...
            LOG.exception(f'unable to write record to Kinesis')

        return response

