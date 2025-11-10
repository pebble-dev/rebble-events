from os import environ

domain_root = environ.get('DOMAIN_ROOT')
http_protocol = environ.get('HTTP_PROTOCOL', 'https')

config = {
    'SQLALCHEMY_DATABASE_URI': environ['DATABASE_URL'],
    'DOMAIN_ROOT': domain_root,
    'DEVELOPER_URL': environ.get('DEVELOPER_URL', f'http://developer.{domain_root}'),
    'HONEYCOMB_KEY': environ.get('HONEYCOMB_KEY', None),
    'DISCORD_HOOK_URL': environ.get('DISCORD_ADMIN_HOOK_URL', None),
    'CORS_HEADERS': 'Content-Type',
}
