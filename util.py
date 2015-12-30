import os
import json
import redis
import requests
from config.config import CONFIG_VARS as cvar
from datetime import datetime


def get_cached_data(cache_key):
    try:
        cached_data = get_cached_value(cache_key)
        if cached_data is not None:
            return json.loads(cached_data)
    except Exception as ex:
        print 'get_cached_data, %s: %s' % (cache_key, ex)


def set_cached_data(cache_key, data, expires=300):
    try:
        set_cached_value(cache_key, json.dumps(data), expires)
    except Exception as ex:
        print 'set_cached_data, %s: %s' % (cache_key, ex)


def get_cached_value(cache_key):
    try:
        return get_cache_db().get(cache_key)
    except Exception as ex:
        print 'get_cached_value, %s: %s' % (cache_key, ex)


def set_cached_value(cache_key, value, expires=300):
    try:
        get_cache_db().setex(cache_key, value, expires)
    except Exception as ex:
        print 'set_cached_value, %s: %s' % (cache_key, ex)


def get_cache_db():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    return redis.from_url(redis_url)


def get_date(date_str):
    try:
        if date_str:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except:
        return None


def get_template(template_name, context):
    try:
        template = fetch_template(template_name)
        if template:
            from jinja2 import Environment, PackageLoader
            env = Environment(loader=PackageLoader('main', 'templates'))
            env.variable_start_string = '<%='
            env.variable_end_string = '%>'
            return env.from_string(template).render(context)

    except Exception as ex:
        print 'get_template %s' % ex


def fetch_template(template_name):
    try:
        cache_key = 'template:%s' % (template_name)
        template = get_cached_value(cache_key)
        if not template:
            template = requests.get(cvar[template_name]).text
            if template:
                set_cached_value(cache_key, template, 300)

        return template

    except Exception as ex:
        print 'fetch_template, %s: %s' % (template_name, ex)


def remove_none(data):
    if not data:
        return
    for (k, v) in list(data.items()):
        if v is None:
            del(data[k])
