"""Pin the 2026-09-12 night RDT census to existing collector gates.

Live campaign roots stay on the box. This module does not accept filings.
"""
import json
import unittest
from pathlib import Path

from .contracts import Refused
from .foundry_output import parsed_json

CENSUS = Path(__file__).resolve().parents[2] / 'docs' / 'v3' / 'construction-swarm' / 'night_rdt_20260912.json'


class NightRdt20260912Tests(unittest.TestCase):
    def setUp(self):
        self.census = json.loads(CENSUS.read_text(encoding='utf-8'))

    def test_filings_remain_unaccepted(self):
        self.assertIs(self.census['accepted'], False)
        self.assertEqual(self.census['source_commit'],
                         'd6d8f19aa682bf3e4d3186de2ad34b974a4d4df3')
        self.assertIn('https://github.com/NotSkittlz/recursion/pull/125',
                      self.census['follows'])

    def test_water_probe_was_unbound_citation_not_rate_limit(self):
        water = self.census['campaigns'][0]
        self.assertEqual(water['run_id'], 'foundry-rdt-water-probe')
        self.assertTrue(water['cognition_answered'])
        self.assertFalse(water['rate_limited'])
        self.assertIn('unbound evidence citation', water['error'])

    def test_wave11_was_a_returning_eight(self):
        wave11 = self.census['campaigns'][1]
        self.assertEqual(wave11['run_id'], 'foundry-rdt-wave11')
        self.assertEqual(wave11['returned'], 8)
        self.assertEqual(wave11['failed'], 0)

    def test_wave12_json_fence_matches_parser_refusal(self):
        wave12 = self.census['campaigns'][2]
        self.assertEqual(wave12['returned'], 29)
        self.assertEqual(wave12['failed'], 1)
        self.assertEqual(wave12['failed_job'], 'research-exactly-one-json')
        self.assertIn('exactly one JSON filing required', wave12['error'])
        with self.assertRaises(Refused):
            parsed_json('```json\n{"a":1}\n```\n```json\n{"b":2}\n```')

    def test_do_not_step_to_fifty_from_this_census(self):
        self.assertEqual(self.census['limits']['next_devin_width'], 30)
        self.assertTrue(self.census['limits']['do_not_admit_50_until_returning_30_reviewed'])
        self.assertEqual(self.census['limits']['reset_credits_used'], 0)
