# Behavioral Checks: Integrated Skill Fix

Use temporary copies. `/SKILL-fix` is a legacy disabled entry; exercise repair via `/SKILL-lint`.

1. **Audit only:** introduce a concrete contradictory scope rule, run audit only, and inspect the proposed diff. The file must remain unchanged until approved; a single approval request follows the concrete proposal.
2. **Already authorized:** ask to fix that scoped defect. Apply the minimal change and re-lint without requesting the same permission twice. Unrelated files/configuration remain outside scope.
3. **Rejected proposal:** reject a shown proposal. No edits occur.
4. **N/A or unknown:** provide a concise correct skill or incomplete session evidence. No persona/examples/anti-hallucination boilerplate is inserted to improve a fixed 9/9 score; missing evidence is not manufactured.
5. **Execution deviation:** a trace ignores a correct rule. Preserve the correct skill; report runtime deviation separately unless another supported defect warrants a change.
6. **Applied vs proposed:** a proposed diff is counted as proposed, not applied. Failed writes remain failed. Re-linting changed instructions does not relabel a historical failure as successful execution.
7. **Round limit:** an unresolved defect remains after two apply-and-validate cycles (`fix.max_rounds = 2`). Stop and report it; do not initiate round three.
8. **Compatibility:** pass legacy results without applicability/source evidence. Re-lint first rather than blindly repairing every non-Pass field.
9. **Literal preservation:** under local-english, a Chinese heading may be translated but a real Chinese filename or command argument stays exact.
