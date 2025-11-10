from flask import Blueprint, jsonify, request, url_for, make_response
from flask_cors import cross_origin
import requests
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from .models import db, Event
from .utils import api_error
from .settings import config
from .discord import announce_new_event
from feedgen.feed import FeedGenerator

import beeline

api = Blueprint('api', __name__)

@api.route('/events/submit', methods=['POST'])
@api.route('/events/submit.json', methods=['POST'])
def submit_event():
    try:
        event_json = request.form
        event = Event.from_json(event_json)
    except ValueError:
        beeline.add_context_field('event.failure.cause', 'from_json')
        return api_error(400)

    db.session.add(event)
    db.session.commit()

    announce_new_event(event)

    result = {
        'message': 'Thank you for the submission!'
    }

    return jsonify(result)


@api.route('/events/approve/<event_id>')
def approve_event(event_id):
    api_key = request.args.get('api_key')
    if not api_key:
        beeline.add_context_field('event.failure.cause', 'api_key')
        abort(401)

    event = Event.query.filter_by(id=event_id, api_key=api_key).one_or_none()

    if not event:
        beeline.add_context_field('event.failure.cause', 'no_event')
        abort(404)

    beeline.add_context_field('event', event.id)

    event.approved = True
    db.session.add(event)
    db.session.commit()

    return 'OK'


@api.route('/events/locations')
@api.route('/events/locations.json')
@cross_origin()
def locations():
    # I'm not aware of any significant locations for the Pebble Community
    return jsonify([])


@api.route('/events/upcoming')
@api.route('/events/upcoming.json')
@cross_origin()
def upcoming_events():
    try:
        limit = int(request.args.get('limit', 60))
        start_date = datetime.strptime(request.args.get('start', date.today().strftime("%Y/%m/%d")), "%Y/%m/%d")
        end_date = datetime.strptime(request.args.get('end', (date.today() + relativedelta(months=6)).strftime("%Y/%m/%d")), "%Y/%m/%d")
    except ValueError:
        beeline.add_context_field('event.failure.cause', 'args')
        return api_error(410)

    events = Event.query.filter(Event.start_date <= end_date, Event.end_date >= start_date, Event.approved == True).order_by(Event.start_date.asc()).limit(limit)
    return jsonify([event.to_json() for event in events])


@api.route('/events/upcoming.<feed_type>')
@cross_origin()
def upcoming_events_feed(feed_type):
    try:
        limit = int(request.args.get('limit', 60))
        start_date = datetime.strptime(request.args.get('start', date.today().strftime("%Y/%m/%d")), "%Y/%m/%d")
        end_date = datetime.strptime(request.args.get('end', (date.today() + relativedelta(months=6)).strftime("%Y/%m/%d")), "%Y/%m/%d")
    except ValueError:
        beeline.add_context_field('event.failure.cause', 'args')
        return api_error(410)

    feed = FeedGenerator()
    feed.id(config.get('DEVELOPER_URL') + '/community/events')
    feed.title('Upcoming Events')
    feed.description('List of upcoming Pebble related events all around the world!')
    feed.link( href=url_for('api.upcoming_events_feed', feed_type=feed_type, _external=True), rel='alternate' )
    feed.logo('https://rebble.io/images/favicon.ico')
    feed.link( href=url_for('api.upcoming_events_feed', feed_type=feed_type, _external=True), rel='self' )
    feed.language('en')

    events = Event.query.filter(Event.start_date <= end_date, Event.end_date >= start_date, Event.approved == True).order_by(Event.start_date.asc()).limit(limit)
    for event in events:
      entry = feed.add_entry()
      event_url = config.get('DEVELOPER_URL') + '/community/events/#event-' + str(event.id)
      entry.id(event_url)
      entry.title(event.title)
      entry.link(href=event_url)
      entry.description(f"Where? {event.location_text}.\nWhen? {event.start_date} - {event.end_date}.\n\n{event.description}")

    if feed_type == 'rss':
        return make_response(feed.rss_str(pretty=True), 200, { "Content-Type": "application/rss+xml" })

    return make_response(feed.atom_str(pretty=True), 200, { "Content-Type": "application/atom+xml" })


@api.errorhandler(404)
def page_not_found(e):
    return api_error(404)


@api.errorhandler(500)
def internal_server_error(e):
    return api_error(500)


def init_api(app, url_prefix=''):
    app.register_blueprint(api, url_prefix=url_prefix)
