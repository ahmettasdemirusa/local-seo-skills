---
name: local-site-migration
description: Redesign, rebuild or move a local business website without losing Google rankings, map visibility or customers' bookmarks. Use when the user is redesigning a site, switching platforms (WordPress, Wix, Squarespace, Shopify, a custom build), changing domain, merging location pages, changing URLs, moving to HTTPS, or saw traffic or calls drop after a relaunch. Covers URL inventory, 301 redirect maps, keeping structured data and NAP intact, Google Business Profile links and Search Console.
license: MIT
metadata:
  version: 1.0.0
  author: Ahmet Tasdemir
---

# Local Site Migration

A redesign is the most common way a local business loses rankings it spent years building. Old URLs start returning 404s, and location pages lose their schema. The Business Profile keeps pointing at a page that no longer exists. Nearly all of this is preventable.

The primary source is Google's guide to site moves with URL changes:
https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

## Google's rules

- **Redirect type:** use server-side **permanent** redirects, 301 or 308. Client-side redirects (JavaScript, meta refresh) are a last resort.
- **Redirect targets:** redirect each old URL to its **most relevant** new URL. Google warns against sending many old URLs to one irrelevant destination such as the home page; it may treat those as soft 404s.
- **Chains:** keep them short, ideally no more than 3 hops.
- **How long:** keep redirects for **at least a year**, and consider keeping them indefinitely. Customers' bookmarks and old links in directories don't expire.
- **After the move:** update canonicals, internal links, sitemaps and any `noindex` rules to the new URLs.
- **Change of Address tool** (Search Console): only for a **domain or subdomain** move. It is not needed for HTTP→HTTPS, www↔non-www or path changes. Submit it for every verified variant of the old domain.

## Before launch

1. **Inventory every old URL.** Combine:
   - the XML sitemap
   - a crawl of the old site
   - Search Console's pages report
   - analytics landing pages
   - the URLs linked from the Google Business Profile, directories and social profiles
   
   Include PDFs, menus, coupons and images people link to.
2. **Find the valuable pages:** those with traffic, links, calls or bookings. For a local business these are usually the home page, the service pages, the location pages and the menu.
3. **Build the redirect map.** Map each old URL to its closest new equivalent, one to one where possible. Only map to a parent page when no equivalent exists.
4. **Carry the local signals over:**
   - the name, address and phone text on every page that had it
   - the LocalBusiness JSON-LD on the home page and every location page (local-business-schema skill)
   - embedded maps, click-to-call links and hours
   - titles and H1s that name the service and the city
5. **Stage and test:**
   - Run `python ../local-seo-audit/scripts/audit.py <staging URL>` on the key pages.
   - Validate the schema in the Rich Results Test.
   - Make sure staging is blocked from indexing, and that the block is removed at launch.

## Launch day

- Deploy the redirects together with the new site. Move all URLs at once; Google recommends this for small and medium sites.
- **Remove the staging `noindex`** or robots block. A leftover block is a common cause of a total drop after launch.
- **Test every mapped redirect.** Each should return one 301 or 308, straight to a 200 page.
- **Update the links you control:**
  - the Google Business Profile website link, for every location
  - social profiles
  - the major directories
  - email signatures and printed QR codes if their URLs changed
- Submit the new sitemap in Search Console. For a domain change, use the Change of Address tool as well.

## The weeks after

- **Watch Search Console daily for the first two weeks:**
  - 404s in the pages report
  - coverage drops
  - which queries fall
- **Check phone calls and bookings,** not just traffic. They are the local metric that matters.
- **Fix every 404** that has traffic or links with a redirect to the right page.
- Some movement in rankings is normal while Google recrawls. A sustained drop usually means missing redirects, lost content or a blocked page. Find which of those it is; don't wait.

## Redirect snippets

```apache
# Apache (.htaccess)
Redirect 301 /our-services/drain-cleaning.html /services/drain-cleaning/
```

```nginx
# Nginx
location = /our-services/drain-cleaning.html { return 301 /services/drain-cleaning/; }
```

- For WordPress, use a redirect plugin or server rules.
- For hosted builders (Wix, Squarespace, Shopify), use the platform's URL redirect manager.
- Match the exact old paths, including trailing slashes and file extensions.
