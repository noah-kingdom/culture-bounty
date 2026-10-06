# CULTURE//BOUNTY

## Tagline
An agent that finds the culturally right creator before everyone else finds the obvious one.

## What it does
CULTURE//BOUNTY is a Cultural Scout Agent for brand partnerships. Give it a brand and a campaign objective. It resolves the brand in Qloo, explores adjacent culture across podcasts, artists, movies and destinations, then deliberately runs a second long-tail search to escape obvious popularity rankings. Qloo explainability stays attached to the agent's reasoning trail.

The agent then selects a culturally aligned creator and converts the discovery into a fail-closed bounty brief:

AUTHORIZE -> verify placement -> CAPTURE
                         \-> VOID

The current hackathon build demonstrates the discovery and decision workflow. It does not execute a real payment.

## Why Qloo
Without Qloo, the product collapses into an LLM making plausible guesses about culture.

Before BUILD, we froze an LLM-only benchmark and ran a live Qloo API gate on Patagonia, Aesop and Liquid Death. Qloo's normal podcast search produced 5/5, 5/5 and 4/5 top-five candidates outside that frozen baseline. A separate low-popularity search produced 5/5 novel candidates for all three brands.

That result changed the project from HOLD to GO.

## Agent workflow
1. Resolve — find the canonical Qloo brand entity.
2. Explore — traverse podcast, artist, movie and destination taste relationships.
3. Diversify — rerun podcast discovery with a popularity cap.
4. Explain — preserve Qloo explainability metadata.
5. Select — choose a long-tail cultural bridge.
6. Brief — generate a creator bounty brief for human approval.

## Who it is for
Brand partnership, sponsorship and creator-marketing teams that want to find adjacent cultural audiences without defaulting to the same celebrity and influencer lists.

## Built with
- Qloo Search API
- Qloo Insights API
- Qloo Explainability
- Python standard-library web server
- Requests

## Testing instructions
Open the live demo. Enter a brand such as Patagonia, Aesop or Liquid Death and a campaign objective, then run the Cultural Scout Agent. Review the agent trace, cross-domain map, long-tail candidates, Qloo Delta panel and generated bounty brief.

No account or payment is required.

## Open source
MIT License.
