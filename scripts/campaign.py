#!/usr/bin/env python3
"""Local, transactional outreach ledger. No network calls or browser automation."""
import argparse
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must include a timezone')
    return result.astimezone(timezone.utc)


def profile(value):
    u = urlparse(value)
    parts = u.path.strip('/').split('/')
    if u.scheme != 'https' or not (u.hostname == 'linkedin.com' or (u.hostname or '').endswith('.linkedin.com')) or len(parts) != 2 or parts[0] != 'in':
        raise ValueError('Expected an HTTPS LinkedIn /in/ profile URL')
    return 'https://www.linkedin.com/in/' + parts[1].lower() + '/'


def connect(directory):
    db = sqlite3.connect(Path(directory) / 'ledger.sqlite', timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.executescript('''
    CREATE TABLE IF NOT EXISTS invitations (
      profile TEXT PRIMARY KEY, state TEXT NOT NULL, at TEXT NOT NULL,
      cohort TEXT NOT NULL, message TEXT NOT NULL, evidence TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT, cohort TEXT NOT NULL, at TEXT NOT NULL,
      decision TEXT NOT NULL, evidence TEXT NOT NULL);
    ''')
    return db


def gate(config, db, now):
    reasons = []
    if config.get('send_authorized') is not True:
        reasons.append('Sending is not authorized')
    if config.get('paused') is not False:
        reasons.append('Campaign is paused')
    if config.get('not_before') and now < stamp(config['not_before']):
        reasons.append('Initial hold has not expired')
    reconciled = config.get('reconciled_at')
    waiver = config.get('history_override', {})
    waived = (waiver.get('approved') is True and bool(waiver.get('user_instruction'))
              and bool(waiver.get('approved_at')) and bool(waiver.get('expires_at'))
              and stamp(waiver['approved_at']) <= now < stamp(waiver['expires_at']))
    if not waived and (not reconciled or not timedelta(0) <= now - stamp(reconciled) <= timedelta(hours=24)):
        reasons.append('Reconcile all known account sends and tracker within 24 hours')
    rows = [dict(r) for r in db.execute('SELECT * FROM invitations')]
    if any(r['state'] in ('reserved', 'unknown') for r in rows):
        reasons.append('Resolve outstanding reservation or uncertain send before continuing')
    sent = [r for r in rows if r['state'] in ('sent', 'already_pending', 'already_connected')]
    local = ZoneInfo(config['timezone'])
    today = sum(stamp(r['at']).astimezone(local).date() == now.astimezone(local).date() for r in sent)
    weekly = sum(now - timedelta(days=7) < stamp(r['at']) <= now for r in sent)
    if any(stamp(r['at']) > now for r in sent):
        reasons.append('Ledger contains future send timestamps')
    if today >= config['daily_cap']:
        reasons.append('Daily cap reached')
    if weekly >= config['rolling_7d_cap']:
        reasons.append('Rolling seven-day cap reached')
    if db.execute("SELECT 1 FROM audit_events WHERE id IN (SELECT MAX(id) FROM audit_events GROUP BY cohort) AND decision='pause'").fetchone():
        reasons.append('An audit has paused outreach')
    cohorts = {}
    for r in sent:
        cohorts.setdefault(r['cohort'], []).append(stamp(r['at']))
    for required in config.get('audit_required_cohorts', []):
        if required not in cohorts:
            reasons.append(f'Import required historical cohort {required} before sending')
    for name, times in cohorts.items():
        audit = db.execute('SELECT * FROM audit_events WHERE cohort=? ORDER BY id DESC LIMIT 1', (name,)).fetchone()
        if len(times) >= config['cohort_size'] or name in config.get('audit_required_cohorts', []):
            eligible = max(times) + timedelta(days=config['audit_wait_days'])
            if now < eligible:
                reasons.append(f'Cohort {name} needs observation until {eligible.isoformat()}')
            elif not audit or stamp(audit['at']) < eligible or stamp(audit['at']) < max(times) or audit['decision'] != 'continue':
                reasons.append(f'Cohort {name} needs a completed continue audit')
    return {'allowed': not reasons, 'reasons': reasons, 'sent_today': today, 'sent_7d': weekly,
            'remaining_today': 0 if reasons else max(0, min(config['daily_cap']-today, config['rolling_7d_cap']-weekly))}


def reserve(config, db, now, url, cohort, message):
    url = profile(url)
    if not message.strip() or len(message.encode('utf-16-le')) // 2 > config['message_limit']:
        raise ValueError('Empty or over-limit message')
    db.execute('BEGIN IMMEDIATE')
    try:
        result = gate(config, db, now)
        if not result['allowed']:
            raise ValueError('; '.join(result['reasons']))
        if db.execute('SELECT 1 FROM invitations WHERE profile=?', (url,)).fetchone():
            raise ValueError('Profile already recorded; inspect rather than retry')
        if db.execute('SELECT 1 FROM audit_events WHERE cohort=?', (cohort,)).fetchone():
            raise ValueError('Use a new cohort ID after an audit')
        active = [r['cohort'] for r in db.execute(
            "SELECT DISTINCT cohort FROM invitations WHERE state IN ('sent','already_pending','already_connected') AND cohort NOT IN (SELECT cohort FROM audit_events)")]
        if any(c != cohort for c in active):
            raise ValueError('Continue the existing unaudited cohort; do not rotate cohort IDs')
        db.execute('INSERT INTO invitations VALUES (?,?,?,?,?,?)',
                   (url, 'reserved', now.isoformat(), cohort, message, 'Awaiting UI result'))
        db.execute('COMMIT')
    except Exception:
        db.execute('ROLLBACK')
        raise
    return {'reserved': url}


def resolve(db, now, url, state, evidence):
    if not evidence.strip():
        raise ValueError('Observed evidence is required')
    url = profile(url)
    db.execute('BEGIN IMMEDIATE')
    try:
        row = db.execute('SELECT * FROM invitations WHERE profile=?', (url,)).fetchone()
        if not row or row['state'] not in ('reserved', 'unknown'):
            raise ValueError('Only an unresolved reservation can be resolved')
        db.execute('UPDATE invitations SET state=?, at=?, evidence=? WHERE profile=?',
                   (state, now.isoformat(), evidence, url))
        db.execute('COMMIT')
    except Exception:
        db.execute('ROLLBACK')
        raise
    return {'profile': url, 'state': state}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign', required=True, type=Path)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    r = sub.add_parser('reserve')
    r.add_argument('profile'); r.add_argument('--cohort', required=True)
    r.add_argument('--message-file', type=Path, required=True)
    r = sub.add_parser('resolve')
    r.add_argument('profile'); r.add_argument('state', choices=['sent','unknown','already_pending','already_connected','not_sent'])
    r.add_argument('--evidence', required=True)
    r = sub.add_parser('import-history')
    r.add_argument('file', type=Path)
    r = sub.add_parser('audit')
    r.add_argument('cohort'); r.add_argument('decision', choices=['continue','pause'])
    r.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    config = json.loads((args.campaign / 'campaign.json').read_text())
    for key in ['daily_cap', 'rolling_7d_cap', 'cohort_size', 'audit_wait_days', 'message_limit']:
        if type(config[key]) is not int or config[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    now = datetime.now(timezone.utc)
    with connect(args.campaign) as db:
        if args.command == 'status':
            result = gate(config, db, now)
        elif args.command == 'reserve':
            result = reserve(config, db, now, args.profile, args.cohort, args.message_file.read_text().strip())
        elif args.command == 'resolve':
            result = resolve(db, now, args.profile, args.state, args.evidence)
        elif args.command == 'audit':
            report = args.report.read_text().strip()
            if not report or not db.execute('SELECT 1 FROM invitations WHERE cohort=? AND state="sent"', (args.cohort,)).fetchone():
                raise ValueError('Nonempty report and a real sent cohort required')
            db.execute('INSERT INTO audit_events (cohort,at,decision,evidence) VALUES (?,?,?,?)',
                       (args.cohort, now.isoformat(), args.decision, report))
            result = {'audit_recorded': args.cohort, 'decision': args.decision}
        else:
            rows = json.loads(args.file.read_text())
            db.execute('BEGIN IMMEDIATE')
            try:
                for r in rows:
                    at = stamp(r['sent_at'])
                    if at > now or not r['evidence'].strip():
                        raise ValueError('History needs past timestamps and evidence')
                    url = profile(r['profile'])
                    old = db.execute('SELECT * FROM invitations WHERE profile=?', (url,)).fetchone()
                    data = (url, 'sent', at.isoformat(), r['cohort'], r['message'], r['evidence'])
                    if old and tuple(old) != data:
                        raise ValueError('History conflicts with existing record: ' + url)
                    if not old:
                        db.execute('INSERT INTO invitations VALUES (?,?,?,?,?,?)', data)
                db.execute('COMMIT')
            except Exception:
                db.execute('ROLLBACK'); raise
            result = {'history_rows': len(rows)}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, sqlite3.Error) as error:
        raise SystemExit(str(error))
