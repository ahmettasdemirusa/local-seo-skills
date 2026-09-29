---
name: location-pages
description: Plan and write location pages and city or service-area landing pages that rank without being doorway pages. Use when the user wants pages for each city, town, neighborhood or service area ("plumber in Springfield", "near me" pages), pages for each branch or location of a multi-location business, or asks whether city pages are spam, how many to make, or how to make them unique. Applies Google's spam policies on doorways, scaled content and keyword stuffing.
license: MIT
metadata:
  version: 1.0.0
  author: Ahmet Tasdemir
---

# Location Pages and Service-Area Pages

Pages for places are legitimate, and often necessary. They are also the most common way local businesses break Google's spam policies. The difference is **whether each page is genuinely useful to someone in that place.**

## The rules that apply

From Google's spam policies (https://developers.google.com/search/docs/essentials/spam-policies):

- **Doorway abuse:** "Doorway abuse is when sites or pages are created to rank for specific, similar search queries." Among Google's examples:
  - "Having multiple domain names or pages targeted at specific regions or cities that funnel users to one page"
  - "Creating substantially similar pages that are closer to search results than a clearly defined, browseable hierarchy"
- **Scaled content abuse:** "Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings and not helping users." It applies no matter how the pages are made, including with AI or templates.
- **Keyword stuffing** includes "Blocks of text that list cities and regions that a web page is trying to rank for."
- **Consequence:** sites that violate these policies "may rank lower in results or not appear in results at all."

Google publishes no uniqueness percentage or word count that makes a page safe. The helpful content guidance says Google does not target a word count. The test is **usefulness**: https://developers.google.com/search/docs/fundamentals/creating-helpful-content

## Two kinds of page

**1. Physical location pages (a branch, office or store).** Always create one per real location. Each needs:

- The location's own name, address and phone, matching its Google Business Profile.
- Its own `LocalBusiness` JSON-LD with `url` set to this page (local-business-schema skill).
- Hours, including holiday hours; an embedded map or directions; and parking or entrance notes.
- What is specific to this location: its staff, services or menu differences, photos of this building, and reviews or testimonials about this location (shown, not marked up as the business's own ratings).
- A link from a "Locations" hub page, so the pages form a clear, browseable hierarchy.

**2. Service-area pages (towns you serve but have no office in).** Create them **only** where you have something true and specific to say about that place:

- Jobs actually done there, e.g. a project gallery with the town named. Get the client's permission, and show no private addresses.
- Local specifics that change the service: housing stock, water hardness, permits and inspections, climate, HOA rules, travel time and fees.
- Testimonials from customers in that town.
- Staff or crews based near there.
- Anything that differs by area: pricing, availability, response times.

If a town's page would only swap the city name into the same text, **don't create it.** Mention the town in a service-area list on one strong page instead: a short, readable list, not a keyword block.

## How many pages?

Start with physical locations, then the handful of towns where the business does the most work and has real material. Add more only when new material exists. Ten useful pages beat two hundred templated ones, and the templated ones put the whole site at risk.

## Page structure

```
H1: {Service} in {City}, {State}. Only as specific as the page really is.
Intro: who you help in {City}, in one or two sentences written for people, not keywords.
Local proof: projects, photos, testimonials from {City}.
What's different in {City}: permits, conditions, pricing, travel.
Services offered here, each linking to its full service page.
Contact: phone, hours, how to book. For a physical location, add the address and a map.
FAQ drawn from real questions customers there ask.
```

- Link each page from the Locations hub or service-area list, and back to the core service pages.
- Don't create orphan pages reachable only from the sitemap.

## Checklist before publishing

- [ ] Would a person in this town find something here that is not on the other location pages?
- [ ] Is every claim true: projects, staff, response times, prices?
- [ ] For a physical location, do the name, address and phone match the Business Profile and the schema exactly?
- [ ] Is the page reachable through normal site navigation?
- [ ] Are there no city lists stuffed into paragraphs or footers?
- [ ] If AI helped draft it, has a person added the local facts and checked every sentence?

## Auditing existing city pages

1. List every city or area page. Compare their main content side by side.
2. **Merge or remove** pages that are near-duplicates. 301-redirect each removed URL to the most relevant remaining page, such as the service page or the nearest location. Don't send them all to the home page (local-site-migration skill).
3. Rewrite the pages worth keeping with real local material.
4. Remove footer or sidebar blocks listing dozens of towns.
