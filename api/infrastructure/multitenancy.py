from werkzeug.wrappers import Request


class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ, shallow=True)
        tenant_id = request.args.get('tenant_id', None)
        if tenant_id:
            tenant = tenant_repository.get_by_id(tenant_id)
            environ['CVTOOL_TENANT'] = tenant
        return self.app(environ, start_response)
