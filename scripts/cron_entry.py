#!/usr/bin/env python3
"""Print a cron entry for review; never installs or changes crontab."""
import argparse
from pathlib import Path
import shlex
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',type=Path,required=True)
p.add_argument('--hour',type=int,default=9)
p.add_argument('--minute',type=int,default=0)
a=p.parse_args()
if not 0 <= a.hour <= 23 or not 0 <= a.minute <= 59: p.error('Invalid hour/minute')
config=a.config.resolve()
if not config.is_file():p.error('Runner config does not exist')
argv=[sys.executable,str(Path(__file__).with_name('run_campaign.py').resolve()),'--config',str(config)]
if any('\n' in v or '\r' in v for v in argv):p.error('Newlines are not supported in cron paths')
print(f'{a.minute} {a.hour} * * * '+shlex.join(argv).replace('%',r'\%'))
