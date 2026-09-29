#!/usr/bin/env python3
"""
Local SEO page audit. Standard library only, Python 3.8+.

Fetches one or more pages of a local business website and checks what matters
for local search: LocalBusiness structured data (against Google's documented
rules), name/address/phone consistency, indexability and on-page basics.

    python audit.py https://example.com/
    python audit.py https://example.com/ https://example.com/locations/springfield/
    python audit.py https://example.com/ --json
    python audit.py --file saved-page.html --url https://example.com/

Exit code: 0 when no errors were found, 1 when at least one error was found,
2 when a page could not be fetched.

MIT License, Ahmet Tasdemir.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

USER_AGENT = "Mozilla/5.0 (compatible; local-seo-audit/1.0; +https://github.com/ahmettasdemirusa/local-seo-skills)"
MAX_BYTES = 5 * 1024 * 1024
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# schema.org types that sit under LocalBusiness. Anything else carrying a
# PostalAddress is reported as "business-like" rather than ignored.
LOCAL_BUSINESS_TYPES = set("""
LocalBusiness AnimalShelter ArchiveOrganization AutomotiveBusiness AutoBodyShop AutoDealer AutoPartsStore AutoRental
AutoRepair AutoWash GasStation MotorcycleDealer MotorcycleRepair ChildCare Dentist DryCleaningOrLaundry
EmergencyService FireStation Hospital PoliceStation EmploymentAgency EntertainmentBusiness AdultEntertainment
AmusementPark ArtGallery Casino ComedyClub MovieTheater NightClub FinancialService AccountingService AutomatedTeller
BankOrCreditUnion InsuranceAgency FoodEstablishment Bakery BarOrPub Brewery CafeOrCoffeeShop Distillery
FastFoodRestaurant IceCreamShop Restaurant Winery GovernmentOffice PostOffice HealthAndBeautyBusiness BeautySalon
DaySpa HairSalon HealthClub NailSalon TattooParlor HomeAndConstructionBusiness Electrician GeneralContractor
HVACBusiness HousePainter Locksmith MovingCompany Plumber RoofingContractor InternetCafe LegalService Attorney
Notary Library LodgingBusiness BedAndBreakfast Campground Hostel Hotel Motel Resort SkiResort VacationRental
MedicalBusiness CommunityHealth Dermatology DietNutrition Emergency Geriatric Gynecologic MedicalClinic Midwifery
Nursing Obstetric Oncologic Optician Optometric Otolaryngologic Pediatric Pharmacy Physician Physiotherapy
PlasticSurgery Podiatric PrimaryCare Psychiatric PublicHealth ProfessionalService RadioStation RealEstateAgent
RecyclingCenter SelfStorage ShoppingCenter SportsActivityLocation BowlingAlley ExerciseGym GolfCourse
PublicSwimmingPool SportsClub StadiumOrArena TennisComplex Store BikeStore BookStore ClothingStore ComputerStore
ConvenienceStore DepartmentStore ElectronicsStore Florist FurnitureStore GardenStore GroceryStore HardwareStore
HobbyShop HomeGoodsStore JewelryStore LiquorStore MensClothingStore MobilePhoneStore MovieRentalStore MusicStore
OfficeEquipmentStore OutletStore PawnShop PetStore ShoeStore SportingGoodsStore TireShop ToyStore WholesaleStore
TelevisionStation TouristInformationCenter TravelAgency
""".split())

FOOD_TYPES = set("FoodEstablishment Bakery BarOrPub Brewery CafeOrCoffeeShop Distillery FastFoodRestaurant "
                 "IceCreamShop Restaurant Winery".split())

MAP_LINK = re.compile(r"(google\.[a-z.]+/maps|maps\.google\.|maps\.app\.goo\.gl|goo\.gl/maps|g\.page/|share\.google/)", re.I)
# North American numbers such as (555) 010-0199 or +1 555.010.0199; other formats are
# still compared through tel: links and the schema.
PHONE_TEXT = re.compile(r"(?<![\d.])(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")


# --------------------------------------------------------------------------- #
# HTML parsing
# --------------------------------------------------------------------------- #

class PageParser(HTMLParser):
    """Collects the handful of things a local SEO audit needs from one page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.canonical = ""
        self.h1 = []
        self.jsonld_raw = []
        self.tel_links = []
        self.map_links = []
        self.map_embeds = []
        self.text_parts = []
        self._stack = []
        self._capture = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)
        if tag == "title":
            self._start_capture("title")
        elif tag == "h1":
            self._start_capture("h1")
        elif tag == "script" and a.get("type", "").strip().lower() == "application/ld+json":
            self._start_capture("jsonld")
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href", "")
        elif tag == "a":
            href = a.get("href", "")
            if href.lower().startswith("tel:"):
                self.tel_links.append(href[4:])
            elif MAP_LINK.search(href):
                self.map_links.append(href)
        elif tag == "iframe":
            src = a.get("src", "") or a.get("data-src", "")
            if MAP_LINK.search(src) or "google.com/maps/embed" in src:
                self.map_embeds.append(src)

    def handle_endtag(self, tag):
        if self._capture and tag == {"title": "title", "h1": "h1", "jsonld": "script"}[self._capture]:
            text = "".join(self._buf)
            if self._capture == "title":
                self.title = " ".join(text.split())
            elif self._capture == "h1":
                self.h1.append(" ".join(text.split()))
            else:
                self.jsonld_raw.append(text)
            self._capture = None
            self._buf = []
        while self._stack and self._stack.pop() != tag:
            pass

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)
        if not self._stack or self._stack[-1] not in ("script", "style", "noscript", "template"):
            self.text_parts.append(data)

    def _start_capture(self, what):
        self._capture = what
        self._buf = []

    @property
    def text(self):
        return " ".join(" ".join(self.text_parts).split())


# --------------------------------------------------------------------------- #
# JSON-LD helpers
# --------------------------------------------------------------------------- #

def types_of(node):
    t = node.get("@type", [])
    t = t if isinstance(t, list) else [t]
    return [str(x).rsplit("/", 1)[-1] for x in t]


def walk(obj):
    """Yield every dict inside a JSON-LD document, including @graph members."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def parse_jsonld(raw_blocks, findings):
    docs = []
    for i, raw in enumerate(raw_blocks, 1):
        try:
            docs.append(json.loads(raw.strip()))
        except ValueError as e:
            findings.append(("error", "schema", "JSON-LD block %d is not valid JSON (%s); search engines ignore it." % (i, e.msg)))
    return docs


def business_nodes(docs):
    nodes, seen = [], set()
    for doc in docs:
        for node in walk(doc):
            if id(node) in seen:
                continue
            ts = types_of(node)
            if any(t in LOCAL_BUSINESS_TYPES for t in ts):
                nodes.append(node)
                seen.add(id(node))
    return nodes


def first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def decimals(v):
    m = re.search(r"\.(\d+)$", str(v).strip())
    return len(m.group(1)) if m else 0


def digits(s):
    d = re.sub(r"\D", "", s or "")
    return d[1:] if len(d) == 11 and d.startswith("1") else d


def bare_host(netloc):
    h = netloc.lower().split(":")[0]
    return h[4:] if h.startswith("www.") else h


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_business(node, page_url, findings):
    """Checks one LocalBusiness node against Google's local business guidelines."""
    label = "/".join(types_of(node))
    add = lambda level, msg: findings.append((level, "schema", "%s: %s" % (label, msg)))

    name = first(node.get("name"))
    if not name:
        add("error", "missing `name` (required by Google).")

    addr = first(node.get("address"))
    if not addr:
        add("error", "missing `address` (required by Google).")
    elif isinstance(addr, str):
        add("warning", "`address` is plain text; use a PostalAddress with separate fields.")
    elif isinstance(addr, dict):
        for field in ("streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry"):
            if not addr.get(field):
                add("warning", "address has no `%s`; Google asks for as many address properties as possible." % field)

    tel = first(node.get("telephone"))
    if not tel:
        add("warning", "no `telephone` (recommended).")
    elif not str(tel).strip().startswith("+"):
        add("tip", "`telephone` should include the country and area code, e.g. +1-555-010-0199.")

    url = first(node.get("url"))
    if not url:
        add("warning", "no `url` (recommended): the URL of this location's own page.")
    else:
        u, p = urlparse(urljoin(page_url, str(url))), urlparse(page_url)
        if u.netloc and p.netloc and bare_host(u.netloc) != bare_host(p.netloc):
            add("warning", "`url` points to another site (%s); it should be this location's own page." % u.netloc)

    geo = first(node.get("geo"))
    if not geo:
        add("tip", "no `geo` coordinates (recommended).")
    elif isinstance(geo, dict):
        lat, lng = geo.get("latitude"), geo.get("longitude")
        if lat is None or lng is None:
            add("warning", "`geo` needs both latitude and longitude.")
        elif decimals(lat) < 5 or decimals(lng) < 5:
            add("warning", "`geo` precision is below 5 decimal places (Google asks for at least 5).")

    pr = first(node.get("priceRange"))
    if pr and len(str(pr)) >= 100:
        add("warning", "`priceRange` is 100+ characters; Google won't show it.")

    hours = node.get("openingHoursSpecification")
    if not hours and not node.get("openingHours"):
        add("tip", "no opening hours (`openingHoursSpecification` is recommended).")
    for spec in (hours if isinstance(hours, list) else [hours] if hours else []):
        if not isinstance(spec, dict):
            continue
        days = spec.get("dayOfWeek", [])
        days = days if isinstance(days, list) else [days]
        for d in days:
            if str(d).rsplit("/", 1)[-1] not in DAYS:
                add("error", "unknown `dayOfWeek` value %r." % d)
        for key in ("opens", "closes"):
            v = spec.get(key)
            if v is None:
                if not (spec.get("validFrom") and spec.get("validThrough")):
                    add("warning", "an opening-hours entry has no `%s`. For Google, mark closed days with opens and closes both \"00:00\"." % key)
            elif not re.match(r"^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$", str(v)):
                add("error", "`%s` value %r is not hh:mm or hh:mm:ss." % (key, v))

    if node.get("aggregateRating") or node.get("review"):
        add("warning", "has `aggregateRating`/`review`. Google does not show review stars for a business "
                       "marking up reviews about itself, including embedded Google or Facebook review widgets. "
                       "Remove it unless this is a third-party site reviewing other businesses.")

    if set(types_of(node)) & FOOD_TYPES:
        if not node.get("servesCuisine"):
            add("tip", "food business without `servesCuisine`.")
        if not (node.get("menu") or node.get("hasMenu")):
            add("tip", "food business without `menu` (the URL of the menu).")

    if types_of(node) == ["LocalBusiness"]:
        add("tip", "generic `LocalBusiness`; use the most specific subtype (Restaurant, Plumber, Dentist...).")


def nap_of(node):
    addr = first(node.get("address"))
    street = addr.get("streetAddress", "") if isinstance(addr, dict) else (addr or "")
    return {
        "name": str(first(node.get("name")) or ""),
        "street": str(first(street) or ""),
        "city": str(addr.get("addressLocality", "")) if isinstance(addr, dict) else "",
        "phone": str(first(node.get("telephone")) or ""),
    }


def analyze_html(html, url, status=200, final_url=None, elapsed=None):
    """Audit one page. Returns a dict with facts and findings; no network access."""
    findings = []
    p = PageParser()
    try:
        p.feed(html)
    except Exception as e:  # malformed markup should not stop the audit
        findings.append(("warning", "page", "HTML could not be fully parsed (%s)." % e))

    final_url = final_url or url
    add = lambda level, area, msg: findings.append((level, area, msg))

    # Indexability and basics
    if status >= 400:
        add("error", "page", "HTTP status %d." % status)
    if not final_url.lower().startswith("https://"):
        add("warning", "page", "Page is not served over HTTPS.")
    if final_url.rstrip("/") != url.rstrip("/"):
        add("tip", "page", "Redirected to %s; link to the final URL directly." % final_url)
    robots = p.meta.get("robots", "") + " " + p.meta.get("googlebot", "")
    if "noindex" in robots.lower():
        add("error", "page", "Page has a `noindex` robots meta tag; it cannot appear in search.")
    if not p.title:
        add("error", "page", "Missing <title>.")
    elif len(p.title) > 70:
        add("tip", "page", "Title is %d characters; it may be cut off in results." % len(p.title))
    if not p.meta.get("description"):
        add("warning", "page", "Missing meta description.")
    if not p.meta.get("viewport"):
        add("warning", "page", "No viewport meta tag; the page may not be mobile-friendly.")
    if not p.canonical:
        add("tip", "page", "No canonical link.")
    if len(p.h1) == 0:
        add("warning", "page", "No <h1> heading.")
    elif len(p.h1) > 1:
        add("tip", "page", "%d <h1> headings; one clear main heading is easier to read." % len(p.h1))

    # Structured data
    docs = parse_jsonld(p.jsonld_raw, findings)
    nodes = business_nodes(docs)
    if not nodes:
        add("warning", "schema", "No LocalBusiness structured data found. Build one with "
                                 "https://ahmettasdemirusa.github.io/local-business-schema-generator/")
    for node in nodes:
        check_business(node, final_url, findings)

    # NAP consistency on the page
    text = p.text
    tel_digits = sorted(set(digits(t) for t in p.tel_links if digits(t)))
    text_phones = sorted(set(digits(m) for m in PHONE_TEXT.findall(text)))
    naps = [nap_of(n) for n in nodes]
    for nap in naps:
        pd = digits(nap["phone"])
        if pd and tel_digits and pd not in tel_digits:
            add("warning", "nap", "Schema phone %s does not match any click-to-call link on the page (%s)."
                % (nap["phone"], ", ".join(tel_digits)))
        if pd and pd not in text_phones and pd not in tel_digits:
            add("warning", "nap", "Schema phone %s is not visible on the page." % nap["phone"])
        if nap["street"] and norm(nap["street"]) not in norm(text):
            add("warning", "nap", "Schema street address \"%s\" is not visible on the page as written." % nap["street"])
        if nap["name"] and norm(nap["name"]) not in norm(text) and norm(nap["name"]) not in norm(p.title):
            add("tip", "nap", "Business name \"%s\" from the schema does not appear in the page text." % nap["name"])
        city = norm(nap["city"])
        if city and city not in norm(p.title) and city not in norm(" ".join(p.h1)):
            add("tip", "page", "City \"%s\" is not in the title or H1. Local pages usually name the place they serve."
                % nap["city"])
    if not p.tel_links:
        add("tip", "nap", "No click-to-call (tel:) link. Mobile visitors expect to tap the number.")
    if not (p.map_links or p.map_embeds):
        add("tip", "nap", "No link to or embed of a Google Maps listing.")

    return {
        "url": url,
        "final_url": final_url,
        "status": status,
        "elapsed_ms": elapsed,
        "title": p.title,
        "h1": p.h1,
        "meta_description": p.meta.get("description", ""),
        "canonical": p.canonical,
        "business_types": ["/".join(types_of(n)) for n in nodes],
        "nap": naps,
        "tel_links": tel_digits,
        "map_links": len(p.map_links) + len(p.map_embeds),
        "findings": [{"level": l, "area": a, "message": m} for l, a, m in findings],
    }


def compare_sites(results):
    """Cross-page NAP consistency: the same business should read the same everywhere."""
    out = []
    by_name = {}
    for r in results:
        for nap in r["nap"]:
            if nap["name"]:
                by_name.setdefault(norm(nap["name"]), []).append((r["url"], nap))
    names = {nap["name"] for r in results for nap in r["nap"] if nap["name"]}
    if len({norm(n) for n in names}) > 1 and len(results) > 1:
        out.append({"level": "tip", "area": "nap", "message": "Different business names across pages: %s. "
                    "Fine for separate locations or brands; otherwise use one consistent name." % ", ".join(sorted(names))})
    for key, entries in by_name.items():
        phones = {digits(n["phone"]) for _, n in entries if n["phone"]}
        streets = {norm(n["street"]) for _, n in entries if n["street"]}
        if len(phones) > 1:
            out.append({"level": "warning", "area": "nap", "message": "\"%s\" has different phone numbers on different pages." % entries[0][1]["name"]})
        if len(streets) > 1:
            out.append({"level": "warning", "area": "nap", "message": "\"%s\" has different street addresses on different pages. "
                        "If these are separate locations, give each its own name and page." % entries[0][1]["name"]})
    return out


# --------------------------------------------------------------------------- #
# Network and output
# --------------------------------------------------------------------------- #

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return body.decode(charset, "replace"), resp.status, resp.geturl(), int((time.time() - start) * 1000)
    except urllib.error.HTTPError as e:
        body = e.read(MAX_BYTES).decode("utf-8", "replace")
        return body, e.code, e.geturl() or url, int((time.time() - start) * 1000)


ICON = {"error": "❌", "warning": "⚠️", "tip": "💡"}
ORDER = {"error": 0, "warning": 1, "tip": 2}


def markdown(results, cross):
    lines = ["# Local SEO audit", ""]
    total = {"error": 0, "warning": 0, "tip": 0}
    for r in results:
        for f in r["findings"]:
            total[f["level"]] += 1
    for f in cross:
        total[f["level"]] += 1
    lines.append("**%d errors · %d warnings · %d tips** across %d page(s)." % (total["error"], total["warning"], total["tip"], len(results)))
    lines.append("")
    for r in results:
        lines.append("## %s" % r["url"])
        lines.append("")
        meta = "HTTP %s" % r["status"]
        if r["elapsed_ms"] is not None:
            meta += " · %d ms" % r["elapsed_ms"]
        if r["business_types"]:
            meta += " · schema: %s" % ", ".join(r["business_types"])
        lines.append(meta)
        lines.append("")
        if not r["findings"]:
            lines.append("No issues found.")
        for f in sorted(r["findings"], key=lambda f: ORDER[f["level"]]):
            lines.append("- %s **%s** · %s" % (ICON[f["level"]], f["area"], f["message"]))
        lines.append("")
    if cross:
        lines.append("## Across pages")
        lines.append("")
        for f in sorted(cross, key=lambda f: ORDER[f["level"]]):
            lines.append("- %s **%s** · %s" % (ICON[f["level"]], f["area"], f["message"]))
        lines.append("")
    lines.append("_Confirm structured data with Google's Rich Results Test: https://search.google.com/test/rich-results_")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit local business web pages for local SEO.")
    ap.add_argument("urls", nargs="*", help="page URLs to audit")
    ap.add_argument("--file", help="audit a saved HTML file instead of fetching (use with --url)")
    ap.add_argument("--url", help="the URL the saved file came from")
    ap.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    args = ap.parse_args(argv)

    # Windows consoles default to a legacy code page that cannot print the report's symbols.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    results, fetch_failed = [], False
    if args.file:
        with open(args.file, encoding="utf-8", errors="replace") as fh:
            results.append(analyze_html(fh.read(), args.url or "https://example.com/"))
    if not args.urls and not args.file:
        ap.error("give at least one URL, or --file")
    for url in args.urls:
        if not re.match(r"^https?://", url):
            url = "https://" + url
        try:
            html, status, final, ms = fetch(url)
            results.append(analyze_html(html, url, status, final, ms))
        except Exception as e:
            fetch_failed = True
            results.append({"url": url, "final_url": url, "status": 0, "elapsed_ms": None, "title": "", "h1": [],
                            "meta_description": "", "canonical": "", "business_types": [], "nap": [], "tel_links": [],
                            "map_links": 0, "findings": [{"level": "error", "area": "page", "message": "Could not fetch: %s" % e}]})

    cross = compare_sites(results)
    if args.json:
        print(json.dumps({"pages": results, "across_pages": cross}, indent=2, ensure_ascii=False))
    else:
        print(markdown(results, cross))

    if fetch_failed:
        return 2
    has_error = any(f["level"] == "error" for r in results for f in r["findings"]) or any(f["level"] == "error" for f in cross)
    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
