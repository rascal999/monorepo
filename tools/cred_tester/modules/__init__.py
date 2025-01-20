# modules/__init__.py

def get_proxy_dict(args):
    """
    Create a proxy dictionary from command line arguments.
    Returns None if no proxy is configured.
    """
    if not hasattr(args, 'proxy') and not hasattr(args, 'http_proxy') and not hasattr(args, 'https_proxy'):
        return None

    proxies = {}
    
    # Handle single proxy for both HTTP and HTTPS
    if hasattr(args, 'proxy') and args.proxy:
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
        return proxies

    # Handle separate HTTP and HTTPS proxies
    if hasattr(args, 'http_proxy') and args.http_proxy:
        proxies['http'] = args.http_proxy
    if hasattr(args, 'https_proxy') and args.https_proxy:
        proxies['https'] = args.https_proxy

    return proxies if proxies else None

def add_proxy_arguments(parser):
    """
    Add proxy-related arguments to an argument parser.
    Supports either a single proxy or separate HTTP/HTTPS proxies.
    """
    proxy_group = parser.add_mutually_exclusive_group()
    proxy_group.add_argument('--proxy', type=str, help='Proxy URL for both HTTP and HTTPS (e.g., http://proxy:8080)')
    proxy_group.add_argument('--http-proxy', type=str, help='HTTP proxy URL (e.g., http://proxy:8080)')
    proxy_group.add_argument('--https-proxy', type=str, help='HTTPS proxy URL (e.g., http://proxy:8080)')
    parser.add_argument('--no-verify', action='store_true', help='Disable TLS certificate verification')
