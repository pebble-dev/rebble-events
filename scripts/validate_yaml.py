#!/usr/bin/env python3

import sys
import yaml
from datetime import date


TYPES = { 'title': str,
    'description': str,
    'website': str,
    'type': str,
    'start_date': date,
    'end_date': date,
    'all_day': bool,
    'location': str,
    'latitude': float,
    'longitude': float }

def load_yaml_from_file(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def validate_location(location):
    for key in ['title', 'description', 'website', 'location', 'latitude', 'longitude']:
        if not key in location:
            sys.exit(f"Location failed! Key {key} doesn't exist!")
    
    for key in location:
        if type(location[key]) != TYPES[key]:
            sys.exit(f"Location '{location['title']}' failed! Key {key} has type '{type(location[key])}', while '{TYPES[key]}' expected!")

    for key in ['latitude', 'longitude']:
        if location[key] < -180 or location[key] > 180:
            sys.exit(f"Location '{location['title']}' failed! {key.title()} out of bounds!")

    print(f"Location '{location['title']}' succeeded")


def validate_locations(infile):
    yaml = load_yaml_from_file(infile)
    if yaml:
        for location in yaml:
            validate_location(location)


def validate_event(event):
    for key in ['title', 'description', 'type', 'start_date', 'end_date']:
        if not key in event:
            sys.exit(f"Event failed! Key {key} doesn't exist!")

    for key in event:
        if type(event[key]) != TYPES[key]:
            sys.exit(f"Event '{event['title']}' failed! Key {key} has type '{type(event[key])}', while '{TYPES[key]}' expected!")

    if not event['type'] in ['Hackathon', 'Meetup', 'Party', 'Other']:
        sys.exit(f"Event '{event['title']}' failed! Wrong event type '{event['type']}'!")

    if not event['end_date'] >= event['start_date']:
        sys.exit(f"Event '{event['title']}' failed! Start date larger than end date!")

    for key in ['latitude', 'longitude']:
        if event[key] < -180 or event[key] > 180:
            sys.exit(f"Event '{event['title']}' failed! {key.title()} out of bounds!")

    print(f"Event '{event['title']}' succeeded")


def validate_events(infile):
    yaml = load_yaml_from_file(infile)
    if yaml:
        for event in yaml:
            validate_event(event)


if __name__ == '__main__':
    validate_locations('locations.yml')
    validate_events('events.yml')
