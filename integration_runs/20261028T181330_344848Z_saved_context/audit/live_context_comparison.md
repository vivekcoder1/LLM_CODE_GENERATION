# Later live-context verification

Post-generation comparison of used frozen inputs with a later live retrieval

**8/8 arms** have matching task, public-code, domain-prior and API-resolution hashes, verified against their saved artifacts.

This check happened after the fresh saved-context experiment. It does not change which context source was actually used for generation.

## Paired context checks

| domain | variant | task_hash_equal | code_context_hash_equal | domain_context_hash_equal | api_resolution_hash_equal | used_files_verified | live_files_verified | generation_input_contexts_equal | core_statistics_equal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | code_only | True | True | True | True | True | True | True | True |
| burgers2d | combined | True | True | True | True | True | True | True | True |
| heat_flow | code_only | True | True | True | True | True | True | True | True |
| heat_flow | combined | True | True | True | True | True | True | True | True |
| julia_set | code_only | True | True | True | True | True | True | True | True |
| julia_set | combined | True | True | True | True | True | True | True | True |
| reaction_diffusion | code_only | True | True | True | True | True | True | True | True |
| reaction_diffusion | combined | True | True | True | True | True | True | True | True |

## New live retrieval: before/after graph topology

| role | before_nodes_count | after_nodes_count | before_relationships_count | after_relationships_count | unchanged_topology_ids | recorded_comparison |
| --- | --- | --- | --- | --- | --- | --- |
| code | 6391 | 6391 | 8483 | 8483 | True | unchanged_topology_ids |
| domain | 108 | 108 | 178 | 178 | True | unchanged_topology_ids |

The table above compares each newly queried database with itself before/after this live retrieval. It does not compare old or restored-database element IDs. Property values were not hashed.

## Chronology

```json
{
  "generation_completed_utc": "2026-10-28T18:16:32.639701+00:00",
  "live_created_utc": "2026-10-28T18:18:03.521330+00:00",
  "live_completed_utc": "2026-10-28T18:21:32.638693+00:00",
  "order": "live_retrieval_started_after_generation_completed"
}
```

## Limitations

- The generated scripts used frozen retrieval inputs. This later check does not retroactively make those generations a live-retrieval experiment.

- Matching hashes establish identical recorded task/code/domain/API-resolution inputs for these arms, not general equivalence of database contents.

- Graph integrity compares element-ID sets and counts only before/after the new live retrieval. Properties are not hashed, and old-versus-restored database IDs are not compared.

- This script performs no API calls, graph queries, generations, executions or credential reads.

## Inputs

```json
{
  "used_manifest": {
    "path": "D:\\Vivek\\research\\integration_runs\\20261028T181330_344848Z_saved_context\\manifest.json",
    "sha256": "01ae70ef48ed4e9ddd3119514cee0a41738eb5d0e881b45d85c21eb023760018"
  },
  "live_manifest": {
    "path": "D:\\Vivek\\research\\integration_runs\\20261028T181803_519861Z\\manifest.json",
    "sha256": "0e1585e0815b9911bbefc91bc7c008c31d631229b7f12f920f642fee0891c32a"
  }
}
```

Full file checks and before/after topology hashes are in [JSON](live_context_comparison.json); paired values are in [CSV](live_context_comparison.csv).
