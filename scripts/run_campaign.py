#!/usr/bin/env python3
"""Run a configured agent in its bound workspace, serialized per distro checkout."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def run(config_path, root=ROOT):
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text())
    argv = config['argv']
    if not isinstance(argv, list) or not argv or any(not isinstance(v, str) or not v for v in argv):
        raise ValueError('argv must be a nonempty string array; shell commands are not supported')
    timeout = config.get('timeout_seconds', 1800)
    if type(timeout) is not int or timeout <= 0:
        raise ValueError('timeout_seconds must be a positive integer')
    campaign = config_path.parent
    if not (campaign/'campaign.json').is_file():
        raise ValueError('Place runner.json beside an initialized campaign.json')
    root = Path(root).resolve()
    workspace = root
    binding_file = campaign/'workspace.json'
    if binding_file.exists():
        binding = json.loads(binding_file.read_text())
        if binding.get('version') != 1:
            raise ValueError('Unsupported workspace binding version')
        for key in ('workspace_root', 'distro_root'):
            if not isinstance(binding.get(key), str) or not Path(binding[key]).is_absolute():
                raise ValueError(f'Workspace binding requires an absolute {key}')
        if Path(binding['distro_root']).resolve() != root:
            raise ValueError('Distro moved; reconcile the campaign binding before running')
        workspace = Path(binding['workspace_root']).resolve(strict=True)
        if not workspace.is_dir():
            raise ValueError('Bound workspace is not a directory')
    runtime = root/'.runtime'
    runtime.mkdir(mode=0o700, exist_ok=True)
    with (runtime/'agent.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Skipped: another agent run holds this checkout lock')
            return 75
        run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:12]
        out = campaign/'runs'/run_id
        out.mkdir(parents=True, mode=0o700)
        prompt = ('Distro root: ' + str(root) + '\nContext workspace: ' + str(workspace)
                  + '\nRead the host workspace instructions, then ' + str(root/'OUTREACH.md')
                  + '. Resolve workflow scripts/docs/skills against the distro root, never the host workspace.\n\n')
        prompt += (root/'prompts/daily.md').read_text()
        prompt += '\n\nSelected campaign directory: ' + str(campaign) + '\nUnattended run: if required user input or authorization is missing, record needs_input in checkpoint.md and stop sends; do not wait indefinitely or invent answers.\n'
        prompt_file = out/'prompt.txt'
        prompt_file.write_text(prompt)
        argv = [v.replace('{prompt_file}', str(prompt_file)) for v in argv]
        status = {'run_id':run_id,'started_at':datetime.now(timezone.utc).isoformat(),'status':'running'}
        status_file = out/'status.json'
        status_file.write_text(json.dumps(status,indent=2))
        start = time.monotonic()
        process = None
        try:
            with (out/'output.log').open('w') as log:
                process = subprocess.Popen(argv, cwd=workspace, stdin=subprocess.PIPE,
                                           stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    process.communicate(prompt.encode(), timeout=timeout)
                    code = process.returncode
                    status['status'] = 'completed' if code == 0 else 'failed'
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL)
                    process.communicate()
                    code = 124
                    status['status'] = 'timed_out'
        except (OSError, KeyboardInterrupt) as error:
            if process is not None and process.poll() is None:
                os.killpg(process.pid,signal.SIGKILL); process.wait()
            code = 130 if isinstance(error,KeyboardInterrupt) else 1
            status.update(status='failed',error=str(error))
        finally:
            status.update(finished_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-start,2))
            if 'code' in locals(): status['exit_code']=code
            status_file.write_text(json.dumps(status,indent=2))
        print(json.dumps({'run':str(out),'status':status['status'],'exit_code':code}))
        return code


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True)
    args=p.parse_args()
    raise SystemExit(run(args.config))
