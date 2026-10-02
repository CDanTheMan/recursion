# Revision 2 correction notes

2026-10-02. This revision supersedes the first delivered packet for implementation reference.

The first R-UI report required supplier-qualified identity in prose but used bare local IDs in several resolved records. That left two suppliers using the same local contribution, input or action name ambiguously linked. This is a specification defect, not an observed runtime failure.

The corrected `recursion.ui-contract@candidate-2`:

- Carries full supplier-plus-local contribution keys through resolved dispositions, nodes, projection bindings and command bindings
- Resolves local fact/action/template/accessibility references only inside their declared qualified namespaces
- Rejects mismatched duplicated contribution and subject fields between a node and its key
- Defines deterministic occurrence indices across nested repetitions and tree-wide node-key uniqueness
- Permits the same local names across different suppliers while refusing duplicates within the same qualified namespace
- Adds corresponding positive and negative fixture predicates

The semantic contribution-point `@1` meanings are unchanged. The previous candidate-1 schema is historical; its identity is not reused for different fields. R-MOB changes only its exact reference to candidate-2. R-PC is unchanged.

The correction received independent static review against the first delivered bytes. All runtime fixtures remain UNEXECUTED. It does not establish implementation behavior, privacy enforcement, performance or a selected technology stack.
