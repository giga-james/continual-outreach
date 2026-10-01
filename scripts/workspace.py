#!/usr/bin/env python3
"""Install workspace loaders or initialize isolated private campaign state."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def workspace_path(value):
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise ValueError('Workspace must be a directory')
    return path


def install(workspace, root=ROOT):
    workspace = workspace_path(workspace)
    root = Path(root).resolve(strict=True)
    if not (root/'OUTREACH.md').is_file():
        raise ValueError('Distro entrypoint OUTREACH.md is missing')
    content = '''---
name: continual-outreach
description: Explore new or hypothetical product ideas, formulate outreach campaigns with optional user-selected workspace context, research qualified prospects, personalize approved outreach, and learn from responses. Invoke for customer discovery and outreach; not ordinary coding tasks.
---

# Continual Outreach

Use the current agent and its tools. Keep this workspace's own instructions in force.
Read the distro entrypoint at Distro root / OUTREACH.md below. Follow its procedure for
intent-first onboarding, optional workspace context and private campaign state.
Offer broad starting suggestions; never assume the current codebase is the product.
Do not treat the distro's AGENTS.md as a replacement for this workspace's instructions. If the distro moved, stop and repair this
loader rather than silently using a different installation.

'''
    content += 'Distro root: ' + json.dumps(str(root)) + '\n'
    content += 'Context workspace: ' + json.dumps(str(workspace)) + '\n'
    targets = [workspace/p/'continual-outreach'/'SKILL.md'
               for p in ('.agents/skills', '.claude/skills')]
    # Preflight every target before writing anything. Do not clobber another skill.
    for target in targets:
        if target.exists() and target.read_text() != content:
            raise ValueError(f'Existing loader differs; review it before replacing: {target}')
        for parent in [target, *target.parents]:
            if parent == workspace:
                break
            if parent.is_symlink():
                raise ValueError(f'Refusing to install through a symlink: {parent}')
            if parent != target and parent.exists() and not parent.is_dir():
                raise ValueError(f'Loader parent is not a directory: {parent}')
    for target in targets:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
    return {'workspace': str(workspace), 'loaders': [str(t) for t in targets]}


def initialize(workspace, name, state_home=None, root=ROOT):
    workspace = workspace_path(workspace)
    root = Path(root).resolve(strict=True)
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', name):
        raise ValueError('Campaign name must be a lowercase slug of at most 64 characters')
    home = Path(state_home).expanduser() if state_home else Path.home()/'.local/share/continual-outreach'
    home = home.resolve()
    if home == workspace or workspace in home.parents or home == root or root in home.parents:
        raise ValueError('Portable campaign state must be outside the workspace and distro')
    key = hashlib.sha256(str(workspace).encode()).hexdigest()[:12]
    campaign = home/'workspaces'/key/'campaigns'/name
    binding = {'version': 1, 'workspace_root': str(workspace), 'distro_root': str(root)}
    if campaign.exists():
        if not (campaign/'campaign.json').is_file() or not (campaign/'workspace.json').is_file():
            raise ValueError('Incomplete campaign exists; recover it rather than overwriting')
        if json.loads((campaign/'workspace.json').read_text()) != binding:
            raise ValueError('Existing campaign binding differs; reconcile before reusing it')
    else:
        campaign.mkdir(parents=True, mode=0o700)
        config = json.loads((root/'examples/campaign.json').read_text())
        config['name'] = name
        (campaign/'campaign.json').write_text(json.dumps(config, indent=2)+'\n')
        (campaign/'workspace.json').write_text(json.dumps(binding, indent=2)+'\n')
        (campaign/'checkpoint.md').write_text('# Campaign checkpoint\n\nDraft only. Establish the user’s chosen idea and context sources, then complete the interview before sending. Do not assume the workspace is the product.\n')
    return {'campaign_dir': str(campaign), **binding}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    add = subs.add_parser('install', help='Add skill loaders without changing host instruction files')
    add.add_argument('--workspace', type=Path, default=Path.cwd())
    init = subs.add_parser('init', help='Initialize private state outside the source workspace')
    init.add_argument('--workspace', type=Path, default=Path.cwd())
    init.add_argument('--name', required=True)
    init.add_argument('--state-home', type=Path)
    args = parser.parse_args()
    try:
        result = (install(args.workspace) if args.command == 'install' else
                  initialize(args.workspace, args.name, args.state_home))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
