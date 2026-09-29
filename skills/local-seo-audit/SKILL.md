---
name: local-seo-audit
description: Audit a local business's search presence and produce a prioritized fix list. Use when the user asks to audit, review or check local SEO, "why isn't my business showing up on Google Maps", "local pack", "map pack", "near me" rankings, NAP consistency, or a website for a restaurant, contractor, clinic, law firm, salon, store or any business with a physical location or service area. Runs a bundled page checker (structured data, NAP, indexability), then walks through the Google Business Profile and reviews. For writing schema see local-business-schema; for the profile itself see google-business-profile.
license: MIT
metadata:
  version: 1.0.0
  author: Ahmet Tasdemir
---

# Local SEO Audit

You are auditing how well a local business can be found in Google Search and Google Maps. Findings must be specific, verifiable and ranked by impact. Never invent a problem you did not observe, and never promise rankings.

## How Google ranks local results

Google's own explanation is that local results are based mainly on **relevance, distance and prominence**: how well the profile matches the search, how far the business is from the searcher, and how well known it is (links, reviews, ratings). Google also states that nobody can pay for a better local ranking. Source: https://support.google.com/business/answer/7091

You cannot change distance. Every recommendation should improve relevance (complete, accurate information) or prominence (reviews, reputation, links, a strong website).

## Step 1: Gather context

Ask only for what you cannot find yourself:

1. Website URL, and the URLs of any location or service-area pages.
2. Business type, and whether customers **visit the business** (storefront), the business **travels to customers** (service-area business), or both.
3. Number of locations.
4. The Google Business Profile, as a Maps link or the exact business name and city.
5. Main services and the towns they want to be found in.

## Step 2: Run the page checker

Run the bundled script on the home page and on every location or contact page:

```bash
python scripts/audit.py https://example.com/ https://example.com/contact/
```

- It needs only Python 3.8+ and no packages.
- Add `--json` for machine-readable output.
- For a page you cannot reach, use `--file page.html --url <original url>`.
- Exit code 1 means at least one error was found; exit code 2 means a page could not be fetched.

It checks:

- **Indexability:** HTTP status, HTTPS, redirects, `noindex`, title, meta description, viewport, canonical, H1.
- **LocalBusiness structured data**, against Google's documented rules:
  - `name` and `address` are required.
  - Full PostalAddress fields.
  - Phone includes the country code.
  - `geo` has at least 5 decimal places.
  - `priceRange` is under 100 characters.
  - Opening hours are valid.
  - The business does not mark up reviews of itself.
  - The most specific subtype is used.
- **NAP on the page:** the schema phone matches the click-to-call link and is visible; the street address is visible; there is a Maps link or embed.
- **Across pages:** the same business has the same phone and address everywhere.

Read the output. Then **verify anything surprising by hand** before you report it, e.g. fetch the page and look at the JSON-LD yourself. The script is a first pass, not the final word.

## Step 3: Review what the script can't see

Work through these with the user or with what you can observe:

**Google Business Profile.** Use the google-business-profile skill for detail.
- Claimed and verified.
- Name matches real-world signage, with no added keywords.
- Primary category is the most specific one.
- Hours are current.
- Service-area businesses hide their address.
- Photos are recent.
- Website link goes to the right page.

**Reviews.** Use the review-management skill.
- Review volume and recency compared with the competitors in the map pack.
- Owner replies.
- Nothing that breaks Google policy or the FTC rule, such as incentives, gating or staff reviewing their own business.

**Website content**
- A clear page for each core service.
- A page for each physical location.
- Location pages are useful and not doorway pages; see the location-pages skill.
- Name, address and phone are visible in text, not only in an image.

**Consistency elsewhere**
- The name, address and phone on major directories and social profiles match the website and the Business Profile.
- If the business moved or rebranded, the old details are the most common source of conflicts.

**Technical**
- Mobile usability.
- Page speed.
- Old URLs redirect after a redesign; see the local-site-migration skill.

## Step 4: Report

Lead with the three changes that will matter most. Then list the rest by severity:

| Severity | Meaning |
|---|---|
| Critical | Blocks visibility: `noindex`, the page does not load, an unverified or suspended profile, invalid structured data, wrong phone number |
| High | Loses a clear signal: no LocalBusiness schema, NAP conflicts, wrong primary category, no location page for a real location |
| Medium | Weakens relevance or trust: missing hours, few or old reviews, thin service pages, no Maps link |
| Low | Polish: coordinate precision, title length, a generic LocalBusiness type |

For each item, give:
- what you observed, with the URL or evidence
- why it matters, citing the official source where one exists
- the exact fix

End by offering to make the fixes, e.g. writing the JSON-LD with the local-business-schema skill.

## Rules

- **Don't guarantee rankings.** Structured data makes a page eligible for features; it does not guarantee them.
- **Don't recommend these, ever:**
  - keyword-stuffed business names
  - fake addresses or virtual offices for a profile
  - review incentives, gating or fake reviews
  - near-duplicate city pages
  
  Each can get the profile suspended, the site demoted or, for reviews in the US, draw FTC penalties. Explain why when the user asks for one.
- Prefer the business's own verifiable facts over generic advice.
