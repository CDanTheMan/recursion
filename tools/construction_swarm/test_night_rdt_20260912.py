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

    def test_wave13_was_a_returning_thirty(self):
        wave13 = self.census['campaigns'][3]
        self.assertEqual(wave13['run_id'], 'foundry-rdt-wave13')
        self.assertEqual(wave13['returned'], 30)
        self.assertEqual(wave13['failed'], 0)
        self.assertFalse(wave13['rate_limited'])
        self.assertEqual(
            wave13['compact_sha256'],
            '00adf22ad00177c6198e4b20511cd8ff2ad7415e4d612388ef932d9a53a7b1b9',
        )

    def test_wave14_json_fence_matches_parser_refusal(self):
        wave14 = self.census['campaigns'][4]
        self.assertEqual(wave14['run_id'], 'foundry-rdt-wave14')
        self.assertEqual(wave14['returned'], 29)
        self.assertEqual(wave14['failed'], 1)
        self.assertEqual(wave14['failed_job'], 'research-output-bytes')
        self.assertFalse(wave14['rate_limited'])
        self.assertIn('exactly one JSON filing required', wave14['error'])
        with self.assertRaises(Refused):
            parsed_json('```json\n{"a":1}\n```\n```json\n{"b":2}\n```')

    def test_wave15_was_a_returning_thirty(self):
        wave15 = self.census['campaigns'][5]
        self.assertEqual(wave15['run_id'], 'foundry-rdt-wave15')
        self.assertEqual(wave15['returned'], 30)
        self.assertEqual(wave15['failed'], 0)
        self.assertFalse(wave15['rate_limited'])
        self.assertEqual(
            wave15['compact_sha256'],
            'ee35fcc74461ba5439cca73fa760dc643a05c7b168fc50e9927a19bd42f42708',
        )

    def test_wave16_json_fence_matches_parser_refusal(self):
        wave16 = self.census['campaigns'][6]
        self.assertEqual(wave16['run_id'], 'foundry-rdt-wave16')
        self.assertEqual(wave16['returned'], 29)
        self.assertEqual(wave16['failed'], 1)
        self.assertEqual(wave16['failed_job'], 'review-output-limit')
        self.assertFalse(wave16['rate_limited'])
        self.assertIn('exactly one JSON filing required', wave16['error'])
        with self.assertRaises(Refused):
            parsed_json('```json\n{"a":1}\n```\n```json\n{"b":2}\n```')

    def test_wave17_was_a_returning_thirty(self):
        wave17 = self.census['campaigns'][7]
        self.assertEqual(wave17['run_id'], 'foundry-rdt-wave17')
        self.assertEqual(wave17['returned'], 30)
        self.assertEqual(wave17['failed'], 0)
        self.assertFalse(wave17['rate_limited'])
        self.assertEqual(
            wave17['compact_sha256'],
            '6d06ee9fe68f77146cd2cbc0a8b54e0ad483fa9951f42959bc0bb5ed6e711364',
        )

    def test_wave18_hit_org_message_rate_limit(self):
        wave18 = self.census['campaigns'][8]
        self.assertEqual(wave18['run_id'], 'foundry-rdt-wave18')
        self.assertEqual(wave18['returned'], 17)
        self.assertEqual(wave18['failed'], 13)
        self.assertTrue(wave18['rate_limited'])
        self.assertEqual(wave18['rate_limit_hits'], 13)
        self.assertIn('overall message rate limit', wave18['error'])
        self.assertEqual(
            wave18['compact_sha256'],
            'de65541e9ca2b9f41949704d306096064fcf61e06d0bef40b348c1284ef662fc',
        )

    def test_do_not_step_to_fifty_from_this_census(self):
        self.assertEqual(self.census['limits']['next_devin_width'], 8)
        self.assertTrue(self.census['limits']['do_not_admit_until_org_rate_limit_clears'])
        self.assertTrue(self.census['limits']['do_not_admit_50_until_returning_30_reviewed'])
        self.assertEqual(self.census['limits']['reset_credits_used'], 0)
