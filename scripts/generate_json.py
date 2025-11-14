#!/usr/bin/env python3

import os
import yaml
import json
from datetime import date

class IsoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


def load_yaml_from_file(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def write_json_to_file(contents, filename):
    with open(filename, 'w') as file:
        print(contents)
        json.dump(contents, file, cls=IsoEncoder)


def generate_locations(infile, outfile):
    yaml = load_yaml_from_file(infile)
    write_json_to_file(yaml, outfile)


def generate_events(infile, outfile):
    yaml = load_yaml_from_file(infile)
    output = {}
    if yaml:
        sorted(yaml, key=lambda d: d['start_date'])
        for event in yaml:
            current_month = [event['start_date'].year, event['start_date'].month]
            end_month = [event['end_date'].year, event['end_date'].month]
            while True:
                calendar_string = '%04d-%02d' % (current_month[0], current_month[1])

                if not calendar_string in output:
                    output[calendar_string] = []

                output[calendar_string].append(event)

                if current_month != end_month:
                    if current_month == 12:
                        current_month = [event.start_date.year + 1, 1]
                    else:
                        current_month = [event.start_date.year, event.start_date.month + 1]
                else:
                    break

        for date in output:
            write_json_to_file(output[date], outfile % date)


def generate_404(contents, outfile):
    write_json_to_file(contents, outfile)


if __name__ == '__main__':
    if not os.path.exists('output'):
        os.makedirs('output')
    generate_locations('locations.yml', 'output/locations.json')
    generate_events('events.yml', 'output/events-%s.json')
    generate_404([], 'output/404.html')
