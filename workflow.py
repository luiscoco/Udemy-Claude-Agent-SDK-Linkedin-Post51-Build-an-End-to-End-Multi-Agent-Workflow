"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    from collections import Counter
    counts = dict(Counter(ticket['topic'] for ticket in data['tickets']))
    plan = await agent.ask('plan', 'Plan a short ticket summary and verification step.', {'goal': data['goal']}, {'steps': ['Count topics', 'Report counts', 'Check evidence']})
    analysis = await agent.ask('analyze', 'Explain only these independently calculated topic counts.', counts, {'top_topic': 'login', 'count': 2})
    if analysis['top_topic'] not in counts or counts[analysis['top_topic']] != analysis['count']:
        raise ValueError('Analysis conflicts with the deterministic count')
    report = await agent.ask('write', 'Write a short report with ticket IDs and the checked counts.', {'tickets': data['tickets'], 'counts': counts, 'analysis': analysis},
                             'Login: 2 tickets (T1, T2). Billing: 1 ticket (T3).')
    accepted = all(ticket['id'] in report for ticket in data['tickets'])
    return {'plan': plan, 'reference_counts': counts, 'analysis': analysis, 'report': report, 'accepted': accepted}
