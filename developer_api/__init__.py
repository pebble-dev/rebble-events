from enum import Enum, unique

from flask import Flask, request
from flask_cors import CORS
from werkzeug.routing import BaseConverter, ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix
from rws_common import honeycomb

from .settings import config
from .api import init_api
from .models import init_app

@unique
class FeedType(str, Enum):
    ATOM = 'atom'
    RSS = 'rss'

class FeedTypeConverter(BaseConverter):

    def to_python(self, value):
        try:
            feed_type = FeedType(value)
            return feed_type
        except ValueError as err:
            raise ValidationError()

    def to_url(self, obj):
        return obj.value

app = Flask(__name__)
cors = CORS(app)

app.url_map.converters.update(feed_type=FeedTypeConverter)
app.config.update(**config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

honeycomb.init(app, 'developer_api')
honeycomb.sample_routes['api.sync'] = 10

init_app(app)
init_api(app)

@app.route('/heartbeat')
@app.route('/developer_api/heartbeat')
def heartbeat():
    return 'ok'
