#!/usr/bin/env python3

import click
import logging
from airtable import airtable
import sys
import uuid
import psycopg2
import psycopg2.extras
sys.path.insert(0, '../auth_api')
from auth_api.lib_cfg import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())
psycopg2.extras.register_uuid()

AIRTABLE_FIELDS = ['Email', 'Metier', 'Valid', 'Reasons', 'Name', 'User type', 'Key', 'pass']
DB_POOL = False

cfg = config.key('postgresql')


def air2dict(res):
    return {
        'name': res['fields'].get('Name'),
        'utype': res['fields'].get('User type'),
        'email': res['fields'].get('Email'),
        'valid': res['fields'].get('Valid'),
        'job': res['fields'].get('Metier'),
        'reasons': res['fields'].get('Reasons'),
        'key': res['fields'].get('Key'),
        'passw': res['fields'].get('pass'),
    }


def pg2dict(res):
    return {
        'name': res.get('name'),
        'email': res.get('email'),
        'valid': res.get('email_valid'),
        'job': res.get('profession'),
        'description': res.get('description'),
        'key': res.get('ukey'),
        'passw': res.get('pass'),
    }


@click.group()
@click.option('--airtable', 'source', flag_value='airtable', default=True)
@click.option('--postgres', 'source', flag_value='postgres')
@click.option('--debug', is_flag=True)
@click.pass_context
def main(ctx, source, debug):
    ctx.ensure_object(dict)
    if debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debugging enabled')
    logger.debug('Source is "%s"', source)
    ctx.obj['source'] = source
    ctx.obj['airtable'] = airtable.Airtable(config.key(['airtable', 'base_id']), config.key(['airtable', 'api_key']))
    ctx.obj['pg'] = psycopg2.connect(config.key(['postgresql', 'dsn']))
    ctx.obj['pg'].autocommit = True


@main.command()
@click.pass_context
def list(ctx):
    if ctx.obj['source'] == 'airtable':
        at = ctx.obj['airtable']
        res = at.get('Test Users')
        for r in res['records']:
            print("""
Name : {name}
    User type: {utype}
    Email : {email}
    Valid : {valid}
    Metier : {job}
    Reasons : {reasons}
    Key : {key}
    pass : {passw}
            """.format(**air2dict(r)))

    if ctx.obj['source'] == 'postgres':
        with ctx.obj['pg'].cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT * FROM users')
            res = cur.fetchall()
            for r in res:
                print("""
Name : {name}
    Email : {email}
    Valid : {valid}
    Metier : {job}
    Description : {description}
    Key : {key}
    pass : {passw}
                """.format(**pg2dict(r)))


@main.command()
@click.pass_context
def migrate(ctx):
    at = ctx.obj['airtable']
    res = at.get('Test Users')
    with ctx.obj['pg'].cursor() as cur:
        for r in res['records']:
            d = air2dict(r)
            logger.debug('Migrating account %s', d['name'])
            d['uuid'] = uuid.uuid4()
            sql = """
            INSERT INTO users (
                userid,
                name,
                username,
                email,
                pass,
                ukey,
                profession,
                description
            ) VALUES (
                %(uuid)s,
                %(name)s,
                %(name)s,
                %(email)s,
                %(passw)s,
                %(key)s,
                %(job)s,
                %(reasons)s
            )"""
            cur.execute(sql, d)


if __name__ == '__main__':
    main()
