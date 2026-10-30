# Research meeting preparation — October 30, 2026

Based on the chat **“Add knowledge graph guidance”** and the saved October 21/28 experiment records. Prepared October 29. Suggested structure assumes a 10-minute progress update followed by discussion.

## Main message

We built a domain-knowledge layer, connected it to the existing code-API knowledge graph, and ran a four-task pilot. The combined pipeline produced finite saved outputs on all four tasks, versus two for code-only retrieval, and corrected a substantial Julia reference-reproduction mismatch. The next research step is to test transfer and isolate whether graph-based retrieval adds value beyond equivalent text guidance.

## Opening you can say aloud (about one minute)

“Since the last update, I’ve added procedural domain knowledge to our existing PhiFlow code knowledge graph pipeline. The code graph tells the model what APIs are available; the domain layer supplies reference-derived information about numerical methods, update order, and state dependencies.

“I compared code-only retrieval with the combined pipeline across Burgers, heat flow, Julia set, and reaction diffusion, generating one fresh script per arm. All eight scripts executed, but numerical checks revealed failures that execution alone missed: the code-only Burgers and heat outputs contained NaNs or infinities, while all combined outputs were finite. The combined Julia output also exactly reproduced the reference, whereas the baseline used a different state-update procedure.

“This is an initial reference-reproduction result. The guidance comes from the evaluation references, and the experiment does not yet isolate graph structure from added information. I’d like feedback on the next ablation study and held-out task design.”

## What was completed

1. **Domain guidance:** reference-derived notes and structured recipes for four available reference simulations. Recipes capture fields, parameters, ordered updates, dependencies, outputs, and API hints. Coverage of the other project domains remains pending where labeled reference sources are unavailable.
2. **Domain graph:** a recorded 108-node, 178-relationship graph. It complements the existing code graph, recorded at 6,391 nodes and 8,483 relationships.
3. **Retrieval integration:** domain API hints guide retrieval of public code documentation. The graphs remain separate; the retrieval layer joins their evidence into the generation context.
4. **Evaluation and provenance:** separate retrieval, generation, execution, output-contract, finiteness, and reference-error reporting; isolated output directories; manifests, hashes, and detailed CSV audits.
5. **Fresh pilot:** eight new generations on October 28 with `claude-sonnet-4-6`, temperature 0, one attempt per arm/task, no retries or manual repairs. The attached offline suite recorded 199 passing tests.

An earlier configuration incident led to explicit credential-file selection and checks against fallback to another graph's credentials. The integration runs recorded database reads only. Mention this briefly if operational reliability is discussed.

## Results to show

| Task | Code-only output | Combined output | Defensible interpretation |
| --- | --- | --- | --- |
| Burgers 2D | Nonfinite from frame 13 | Finite | Observed improvement in saved-output validity; solver accuracy remains unresolved because initial data differ from the reference. |
| Heat flow | Nonfinite from frame 16; explicit step reports a CFL violation | Finite; implicit diffusion | Concrete method-selection difference. Task asks for x-only diffusion; reference and generated operators are multidimensional. |
| Julia set | Finite; RMSE 7.5198 | Finite; RMSE 0; identical reference hash | Strongest substantial reference-reproduction result: persistent state and update sequence differ between arms. |
| Reaction diffusion | Finite; u/v RMSE approximately 3.72e-8 / 4.71e-8 | Finite; both RMSE 0; identical reference hashes | Baseline was already extremely close. Exact reproduction does not establish a meaningful physical-accuracy gain. |

Frames above are zero-based. **Finite output is a diagnostic, not proof of physical correctness.**

Numbers worth remembering: **4 tasks, 8 new scripts, 8 successful executions, finite outputs in 2/4 baseline arms versus 4/4 combined arms.** These are task-arm counts from one pilot, not estimated population success rates.

Retrieval support: documentation retained for the same 13 resolved API hints rose from **2/13 to 13/13** across domain contexts. One additional hint, `field.laplace`, remained unresolved and is excluded from that denominator. This measures documentation coverage.

## Two examples to explain clearly

**Heat: method choice matters.** The baseline uses explicit diffusion with `dt=1`, one substep, and a recorded warning `CFL = 101.0 > 0.5`. The combined script uses implicit diffusion and saves finite temperatures. This is a compelling observed failure case, although the operator mismatch prevents claiming task correctness from the small reference error.

**Julia: state dependencies matter.** The baseline resets its state at each output time and runs 50 inner iterations. The combined script maintains complex state and cumulative counts across 100 updates, following the reference recipe. Its output matches the reference exactly. Both scripts warn about internal complex-state arithmetic; describe their saved counts as finite, rather than all computations as warning-free.

## Likely questions and answers

**What is the research contribution so far?**
We now have an implemented way to connect procedural domain relationships to API retrieval, plus audited failure cases showing why API availability and successful execution are insufficient evaluation criteria. A broader graph-specific effectiveness claim still needs experiments.

**Did the knowledge graph itself cause the improvement?**
That is not isolated yet. The combined arm gets reference-derived procedural information, different retrieved API context, and a larger prompt. Equivalent plain-text guidance is an essential comparison.

**Is this reference leakage?**
The domain recipes were extracted from the same reference programs used for evaluation. This is explicitly a reference-reproduction pilot; it does not test held-out generalization. A transfer study must keep evaluation variants out of graph construction.

**Why not just put the reference code in the prompt?**
That is a useful baseline for reproduction. The hypothesis to test is whether structured retrieval can select reusable procedural evidence and support adaptation with a constrained context budget. The current results do not establish that advantage.

**How controlled is the comparison?**
Tasks, paired base plans/configuration, model, temperature, token limit, and replicate align. Retrieved code context differs intentionally between pipelines. There is one generation per arm, no provider seed, and no variance or significance estimate.

**Were these generated against live graphs?**
Generation used frozen contexts retrieved October 21. A separate October 28 live retrieval afterward returned identical recorded inputs for all eight arms. That validates those inputs but does not change the generation chronology.

**What do the 199 tests prove?**
They support the offline pipeline implementation and reporting. They are separate from the eight generated-script outcomes and do not prove scientific correctness.

**Does zero RMSE mean the physics is correct?**
It establishes agreement with a particular stored reference array. Reference validity and task compliance require their own checks. The heat task/reference disagreement makes this distinction especially important.

## Proposed next experiments — bring these as decisions

1. **Repair the evaluation target first.** Align Burgers initial conditions and randomness. Decide the authoritative heat equation/operator and construct a matching reference. Specify output contracts, task-compliance checks, and numerical tolerances before generation.
2. **Run an ablation study.** Compare code-only retrieval, code plus equivalent plain-text procedural guidance, domain-guided API retrieval without procedural prose, and the full combined pipeline. Match evidence and context budgets where feasible and document remaining differences. Add direct-reference-code context if reference reproduction is an explicit objective.
3. **Test held-out adaptation.** Freeze graph construction, then evaluate unseen changes to parameters, initial conditions, boundaries, resolution, and operators. Start with a clear x-only heat request that conflicts with the multidimensional recipe: does the model follow the task or copy the recipe?
4. **Repeat generations.** Agree on a feasible task count and samples per arm with the lab. Report variation in contract compliance, finiteness, task correctness, eligible reference error, and token usage. Temperature zero alone does not guarantee repeatability.

Suggested question to end with: **“Should the next milestone prioritize demonstrating transfer to held-out task variants, or isolating the benefit of graph-guided retrieval over equivalent text? My proposal is to fix the reference mismatches, then run a small study covering both.”**

## Suggested 10-minute flow

| Time | Focus |
| --- | --- |
| 0–1 min | Research question and opening |
| 1–3 min | What the domain graph contains and how it joins API retrieval |
| 3–6 min | Results table; heat and Julia examples |
| 6–8 min | Reference-derived guidance, one sample, and prompt/context confounds |
| 8–10 min | Proposed experiments and decision requested |

## Tonight's 25-minute rehearsal

- **5 minutes:** practice the opening until you can explain the code graph/domain graph distinction without reading.
- **8 minutes:** explain the heat and Julia examples using the saved code review.
- **7 minutes:** answer the graph-versus-text, reference-leakage, and zero-RMSE questions aloud.
- **5 minutes:** rehearse the ending and open the result table and evidence files below. Use saved evidence for the meeting demonstration.

## Evidence to have open

- [Fresh-generation results](knowledge_context/FRESH_GENERATION_RESULTS.md): primary summary, controls, metrics, limitations, and chronology.
- [Manual script review](integration_runs/20261028T181330_344848Z_saved_context/audit/manual_script_review.md): explanations of method and state-update differences.
- [Pipeline guide](knowledge_context/COMBINED_PIPELINE.md): architecture, graph schemas, retrieval joins, and configuration.
- [Earlier integration results](knowledge_context/INTEGRATION_RESULTS.md): retrieval coverage and historical reruns; keep separate from fresh-generation outcomes.
- [Live-input comparison](integration_runs/20261028T181330_344848Z_saved_context/audit/live_context_comparison.md): later verification of the eight recorded input contexts.
- [Recorded validation summary](integration_runs/validation_20261028T181257_012262Z/summary.json): 199 offline test outcomes.

This preparation used existing chat and local evidence. It did not run new experiments or query the databases.
