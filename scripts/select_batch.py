#!/usr/bin/env python3
"""Plan a reproducible profile-level bandit batch; never sends invitations."""
import argparse
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def timestamp(s):
    t = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if t.tzinfo is None:
        raise ValueError('Timezone-aware timestamps required')
    return t.astimezone(timezone.utc)


def select(data, now, size=10, exploration=0.2, window_days=14, seed=0):
    if not 0 <= exploration <= 1 or size < 1 or window_days < 1:
        raise ValueError('Invalid selection parameters')
    if now.tzinfo is None:
        raise ValueError('Timezone-aware now required')
    candidates = data['candidates']
    observations = data['observations']
    for rows in [candidates, observations]:
        ids = [r['id'] for r in rows]
        if len(ids) != len(set(ids)):
            raise ValueError('One row per prospect per input collection is required')
    contacted = {r['id'] for r in observations}
    pool = [r for r in candidates if r.get('eligible') is True and r['id'] not in contacted]
    if any(not r.get('segment') for r in candidates + observations):
        raise ValueError('Freeze a segment label before sending')
    stats = {}
    censored = 0
    for row in observations:
        deadline = timestamp(row['sent_at']) + timedelta(days=window_days)
        checked = timestamp(row['observed_through']) if row.get('observed_through') else None
        reward = row.get('qualified_reply_within_window')
        # Require the same completed observation window for positives and negatives.
        if now < deadline or checked is None or checked < deadline or checked > now or type(reward) is not bool:
            censored += 1
            continue
        a, b = stats.setdefault(row['segment'], [1, 1])
        stats[row['segment']] = [a + int(reward), b + int(not reward)]
    rng = random.Random(seed)
    size = min(size, len(pool))
    explore_n = min(size, math.ceil(size * exploration))
    selected = []
    for i in range(size):
        arms = sorted({r['segment'] for r in pool})
        if i < explore_n:
            # Uniform across profile segments, not people: large companies cannot
            # absorb the entire exploration budget merely through candidate count.
            arm = rng.choice(arms)
            route = 'explore'
        else:
            draws = {arm: rng.betavariate(*stats.get(arm, [1, 1])) for arm in arms}
            arm = max(draws, key=draws.get)
            route = 'posterior_sample'
        options = sorted([r for r in pool if r['segment'] == arm], key=lambda r: r['id'])
        person = rng.choice(options)
        selected.append({'id': person['id'], 'segment': arm, 'route': route})
        pool.remove(person)
    return {'policy_version': 'profile-bandit-v1', 'seed': seed, 'as_of': now.isoformat(),
            'window_days': window_days, 'exploration_fraction': exploration,
            'censored_observations': censored, 'posteriors': stats, 'selected': selected,
            'note': 'Plan only. Eligibility, authorization, live status and send gate still required.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--size', type=int, default=10)
    p.add_argument('--exploration', type=float, default=0.2)
    p.add_argument('--window-days', type=int, default=14)
    p.add_argument('--seed', type=int, required=True)
    a = p.parse_args()
    print(json.dumps(select(json.loads(a.input.read_text()), datetime.now(timezone.utc),
                            a.size, a.exploration, a.window_days, a.seed), indent=2))
