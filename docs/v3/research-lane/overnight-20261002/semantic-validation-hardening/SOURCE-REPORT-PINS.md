# Semantic validation hardening source and report pins

Prepared 2026-10-02. Evidence status: static synthesis of reviewed reports; target execution false; runtime behavior unknown. The report does not constitute a new independent source audit. Direct repository rereading was unnecessary; repository citations and source hashes below are inherited from the pinned reports and their provenance records. Report bytes were read and hashed locally. All paths are packet-relative or repository-relative, never execution-workspace locations.

## Repository authority

Commit: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

Selected source identities recorded by the input provenance:

| Repository-relative source | SHA-256 |
|---|---|
| `state/DECISIONS.md` | `0e821effc75a40662a5c82e5ce9ffee755eba9240978b12b0c1a2fa1c1354516` |
| `docs/v3/AUTONOMOUS-PLANNING.md` | `f894da5bc3e4e898a16c61e859f5464c614b3ea2b9a4bfb32781c5792d9cfa41` |
| `docs/v3/M1A-WIRE-PROFILE.md` | `8041689e110ccdafb10225181abce52bddda7ac1ea198c0118cc1d8de69f11e0` |
| `docs/v3/M1A-FIXTURE-ORACLES.md` | `b6f40b1f66030e3b8bd311f7a5e928bf8cd7b672fd140404a992b8adc780e07d` |
| `scripts/v3/planning/validation/canonical.py` | `aed2ff3f8ecb281407548735c1ab38c07255be9490b70e4c2d717d2b5d713f5e` |
| `scripts/v3/planning/validation/contracts.py` | `77df3b180846834da5a4e458e3dc29b2bcbe41b6da821ed0ac29c2e88f188185` |
| `scripts/v3/planning/replay/kernel.py` | `9327669e4ae8e2a8b97918c16cf91ec2b96797be78af989dc26939192a345338` |
| `scripts/tests/v3/planning/fixtures/F-M1A-005.json` | `e6b97a33e47977e811290db19ffac4adbb85b9254c4d01a860d0d72655fa4729` |
| `experiments/v3/fu-03-formal-model/RIntegrated.tla` | `2e13b27a4672f5d3c7a4e7924ad11eee7e71dbd9bef2960d58676783891cab38` |
| `experiments/v3/fu-03-formal-model/mutants.py` | `3454ba2c4691478b4541905ef83a0e9cbfcb91453c199291723654d9ece1e831` |
| `docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md` | `609db1246e969d90afa7fac56970be96aff88f4a8893b47b981c05f04f87fbc7` |

Full source inventories remain in the supplemental manifest and semantic coverage matrix pinned below. The supplemental report's actual digest matches its manifest entry; the SG report and matrix actual digests match their supplied checksum record. Those matches establish byte identity, not semantic correctness.

## Directly consumed report identities

SHA-256 followed by packet-relative path:

eae6444e59169e5908d2f0a8a058930b98d28054c0d0fb27e7cd95cd3e0a9b56  additional-kernel-research/SUPPLEMENTAL-KERNEL-AUDIT.md
a4f0999126284e46b4a9d513c0963668345a4f0900df5c27058d167d80719b68  additional-kernel-research/SOURCE-MANIFEST.json
bce322e7917c4223f8ece5aa2e78b4a03d4ff8f6853f59ddcaf05e18b6feb426  semantic-guard-research/SEMANTIC-GUARD-COVERAGE.md
5d574b79d6bade26b7e267177d41bd11657374a157a6452085dc90b37e5d579a  semantic-guard-research/coverage-matrix.json
0c644e61adb14505ef449c39bb4b70f2b0a9f9622d61b80b10d2b26e4035028a  semantic-guard-research/SHA256SUMS.txt
370ffa900baba30676504c28e4a8b54b8a8e3a0c39ae7128c2d91307bc570fb3  synthesis/MODEL-ARCHITECTURE.md

## Deliverable identity
The SG report and matrix pins include the SG06 and shared packet-correlation prefix-validity clarifications read before finalization.
The supplemental report and manifest pins include the 10:31 UTC SK02 diagnostic-seed clarification, reread before this refresh; SK01 remains unaffected on the packet-correlation axis only.


No target imports, execution, new tests, model checking, provider/harness calls, installs, source edits or frozen main-packet changes were performed. Local text reading, hashing and separate artifact writing only.
52236b00224039ab47c2a23f427d93b69d7abba5836150e240924010f68d49bf  semantic-validation-hardening/SEMANTIC-VALIDATION-HARDENING.md
