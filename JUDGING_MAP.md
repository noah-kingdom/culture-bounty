# Judging Map

## 1. Technological Implementation
- Live Qloo /search entity resolution.
- Live /v2/insights across four cultural domains.
- Qloo explainability preserved per recommendation.
- A separate low-popularity podcast pass deliberately changes the search policy.
- The agent exposes its decision trace rather than returning a static recommendation.

## 2. Design
- Single-page product flow.
- Clear six-stage agent trace: Resolve -> Explore -> Diversify -> Explain -> Select -> Brief.
- Cross-domain taste map plus long-tail section.
- Qloo Delta panel for benchmark brands.
- Human approval is intentionally preserved before external action.

## 3. Potential Impact
Problem: brand/creator matching is dominated by obvious popularity lists and manual intuition.

Target user: brand partnerships / sponsorship / creator-marketing teams.

Outcome: discover culturally aligned but less obvious creators, then convert the result directly into a verified bounty brief.

## 4. Quality of the Idea
The product does not ask Qloo for "more recommendations." It changes the agent's action policy:
- cultural grounding from Qloo;
- explicit long-tail search;
- explainability attached to the selection;
- fail-closed creator bounty workflow.

The core claim was tested before BUILD against a frozen LLM-only baseline and passed on 3/3 brands.
