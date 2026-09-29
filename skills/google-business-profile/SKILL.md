---
name: google-business-profile
description: Set up, optimize or fix a Google Business Profile (formerly Google My Business) within Google's guidelines. Use when the user asks about their Google Business Profile, GBP, GMB, Google Maps listing, business name, categories, service areas, hiding the address, business description, hours, photos, posts, products, services, a suspended or disabled profile, a practitioner profile, or "how do I rank on Google Maps". Explains what is allowed, what gets profiles suspended, and which features Google has retired.
license: MIT
metadata:
  version: 1.0.0
  author: Ahmet Tasdemir
---

# Google Business Profile

The Business Profile is what appears in Google Maps and the local pack. Your job is to make it **complete, accurate and compliant**. Most suspensions come from guideline violations the owner did not know about.

The primary source is Google's "Guidelines for representing your business on Google":
https://support.google.com/business/answer/3038177

Google changes these pages often. Re-read them before giving a definitive answer on an edge case, and link the user to the page.

## Business name

- **Use the real-world name** exactly as it appears on signage, the website, stationery and invoices.
- **Adding "unnecessary information" is not allowed** and can get the profile suspended. That means no:
  - marketing taglines
  - store codes
  - ® or ™ signs
  - hours or phone numbers
  - URLs
  - service or product keywords
  - location words
  - "inside X" (containment)
  - all-caps words
  
  Legal suffixes such as LLC or Inc., and special characters, need real-world proof such as signage or invoices.
- Google's own examples: "Midas Auto Service Experts" becomes "Midas"; "Equinox near SOHO" becomes "Equinox SOHO".
- **Chains:** use the same name for every location in a country, except for sub-brands and locations whose signage consistently differs.

If the user wants keywords in the name "because competitors do it", explain the suspension risk. The safe path is to report competitors' violations through Google's tools, not to copy them.

## Address and service areas

| Business type | What to do |
|---|---|
| **Storefront** (customers visit) | Show the address. It needs permanent, fixed signage. No URLs or keywords in address lines. |
| **Service-area business** (you go to customers) | **Hide the address.** Google's example is a plumber working from home. Keep one profile for the central office, with a service area. |
| **Hybrid** (both) | Show the staffed location and add a service area. |

**Not eligible:**
- P.O. boxes and mailboxes at remote locations
- virtual offices, i.e. a rented mailing address the business does not operate from
- co-working spaces without signage, customer hours and your own staff present

**Service areas:**
- Up to 20, set by city or postal code (https://support.google.com/business/answer/9157481).
- A radius is not allowed.
- Keep it within about 2 hours' drive of the base.
- A separate profile per location is allowed only when each location has its own service area and staff.

**One profile per business or location.** No duplicates, whether in one account or several. Co-located businesses each get their own profile, e.g. a restaurant inside a hotel or a pharmacy inside a supermarket.

## Categories

- **The primary category** matters most for relevance. It is the first one entered, and up to 9 more can be added (https://support.google.com/business/answer/14368911).
- **Use as few categories as possible,** each as specific as possible.
- **Test each one:** "this business **is a** ___", not "this business **has a** ___".
- **Categories are not keywords.** Use attributes, services and the description for extra detail.

## Description, phone, website, menu

- **Description:** up to 750 characters, with no URLs or HTML. Describe the business itself: what it does, what it's known for, the areas it serves. Don't make it about promotions, prices or sales, and don't use gimmicky characters.
- **Phone:**
  - It must reach that specific location; prefer a local number over a call centre.
  - The business must control the number, and it can't be a premium-rate number.
  - Use the same number as the website and the LocalBusiness schema.
- **Website:** link the page for **that location**; on a multi-location site that is the location page, not the home page. It can't be a URL that redirects elsewhere, including a social media page.
- **Menu links** can't point directly to third-party ordering or delivery services.

## Practitioners

Doctors, dentists, lawyers, financial planners, and insurance and real-estate agents may have their own profile if they are public-facing and reachable at the verified location during stated hours. Support staff and lead-generation agents may not.

- **Several practitioners at one location:** the organization has its own profile.
- **A solo practitioner at a branded location:** use "[brand]: [practitioner name]", e.g. "Allstate: Joe Miller".
- **Titles:** Dr., MD and Esq. are allowed.

## Hours, photos, posts, products, services

- **Hours:** keep regular hours current, and set special hours for holidays so customers don't find a closed door.
- **Photos:** add real, recent photos: exterior (it helps people find the entrance), interior, team, work and products.
- **Posts** are **active**. There are Updates, Offers and Events. Posts older than 6 months are archived unless they have a date range. (https://support.google.com/business/answer/7342169)
- **Services** are **active** for eligible categories. Service names must not contain prices, phone numbers or personal information. (https://support.google.com/business/answer/9455399)
- **Products** are **active**, but must follow Google's Shopping ads policy. Regulated items such as alcohol, tobacco and pharmaceuticals are not allowed. (https://support.google.com/business/answer/9124203)

## Retired or changed features (as of 2026)

Don't tell users to use these:

- **Chat / messaging:** retired July 31, 2024. In select regions, customers can now contact businesses by text or WhatsApp instead. (https://support.google.com/business/answer/14919056)
- **Business Profile websites** (business.site): retired. Link an external website instead.
- **Q&A:** changed.
  - The Q&A API was discontinued on November 3, 2025 (https://developers.google.com/my-business/content/qanda/change-log).
  - Google's help pages now describe Q&A as limited to select categories and regions.
  - Check the current help page before advising on it.

## Ranking

Google says local results are based mainly on **relevance, distance and prominence**. Prominence comes partly from links and from the number and rating of reviews. Google also says there is no way to pay for a better local ranking (https://support.google.com/business/answer/7091).

Practical order of work:
1. Verify the profile.
2. Complete every relevant field accurately.
3. Choose the right primary category.
4. Earn reviews steadily and reply to them (review-management skill).
5. Keep the website consistent with the profile (local-business-schema skill).
6. Build real local reputation.

## Suspensions

If a profile is suspended or disabled:
1. Compare it with the guidelines above: name, address eligibility, service-area setup, duplicates.
2. Fix every violation first.
3. Then appeal through Google's official process, with evidence: signage photos, a business license, utility bills.

Never create a new profile to get around a suspension.
