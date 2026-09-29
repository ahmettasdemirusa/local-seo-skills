# Local SEO Skills: instructions for AI agents

This repository contains Agent Skills for local SEO. Each folder in `skills/` holds a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.

When a task involves the local search presence of a business with a physical location or a service area, read the matching skill **before** answering:

| Task | Skill |
|---|---|
| Audit a local business website or its Google/Maps visibility | `skills/local-seo-audit/SKILL.md` (run `skills/local-seo-audit/scripts/audit.py <url>`) |
| Write or fix LocalBusiness JSON-LD / schema markup | `skills/local-business-schema/SKILL.md` |
| Google Business Profile (GBP/GMB): name, categories, service areas, suspensions | `skills/google-business-profile/SKILL.md` |
| Getting or replying to reviews; review incentives; fake reviews | `skills/review-management/SKILL.md` |
| City, service-area or location landing pages | `skills/location-pages/SKILL.md` |
| Redesigning, re-platforming or moving a local business site | `skills/local-site-migration/SKILL.md` |

Ground rules that apply to every skill:

- **Cite the official source** linked in the skill when you state a rule.
- **Don't guarantee rankings or rich results.**
- **Never recommend guideline or legal violations:** keyword-stuffed business names, fake or virtual addresses, review incentives or gating, fake reviews, or near-duplicate city pages. If asked, explain the risk and offer the compliant alternative.
- **Use only the business's real, verifiable information.** Never invent coordinates, hours, reviews or claims.
