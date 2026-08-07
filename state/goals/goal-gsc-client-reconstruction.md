schema_version: 1
id: goal-gsc-client-reconstruction
project_id: golden-stallion-client
status: active
outcome: Reduce verified client-reconstruction gaps through the existing conformance and native-diff gates.
acceptance_suite: Existing GSC conformance/native-diff gates named by each task.
falsifier: A task changes a test, fixture, oracle, or baseline to manufacture a green result.
budget: offline machine-gated work only; live game access remains human-gated

This goal preserves the proven client and renderer verification paths; it does not authorize a pilot.
