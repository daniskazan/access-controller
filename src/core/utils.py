from django.conf import settings


def get_host(request, with_protocol=False, domain=None):
    """
    Get current backend host and add protocol to host.
    For localhost, there is no information about the protocol in the request
    and for this it is added manually
    """
    host = domain or request.get_host()
    if with_protocol:
        if "://" not in host:
            scheme = "https" if settings.ENVIRONMENT != "local" else request.scheme
            host = f"{scheme}://{host}"
    return host


def build_frontend_host(host):
    if settings.ENVIRONMENT == "local":
        return f"http://{settings.BASE_FRONTEND_HOST}"
    """Split the client's domain at the third level and connect it to an external host."""
    return f"{host.split('.')[0]}.{settings.BASE_FRONTEND_HOST}"


def get_frontend_host(request):
    """Get third level domain and concatenating with base frontend host."""
    return build_frontend_host(get_host(request, with_protocol=True))
