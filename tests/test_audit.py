"""Offline tests for skills/local-seo-audit/scripts/audit.py. Run: python -m unittest discover tests"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "local-seo-audit", "scripts"))
import audit  # noqa: E402

GOOD_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Plumber",
    "name": "Acme Plumbing",
    "url": "https://www.acme-plumbing.example/",
    "telephone": "+1-555-010-0199",
    "address": {"@type": "PostalAddress", "streetAddress": "123 Main Street", "addressLocality": "Springfield",
                "addressRegion": "IL", "postalCode": "62701", "addressCountry": "US"},
    "geo": {"@type": "GeoCoordinates", "latitude": 39.78172, "longitude": -89.65015},
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Friday"], "opens": "08:00", "closes": "17:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "00:00", "closes": "00:00"},
    ],
}


def page(schema=GOOD_SCHEMA, body=None, head_extra=""):
    blocks = ""
    if schema is not None:
        blocks = '<script type="application/ld+json">%s</script>' % (schema if isinstance(schema, str) else json.dumps(schema))
    body = body if body is not None else (
        '<h1>Plumber in Springfield, IL</h1>'
        '<p>Acme Plumbing · 123 Main Street, Springfield, IL 62701</p>'
        '<a href="tel:+15550100199">(555) 010-0199</a>'
        '<a href="https://maps.app.goo.gl/abc">Directions</a>')
    return ('<!doctype html><html><head><title>Acme Plumbing | Plumber in Springfield, IL</title>'
            '<meta name="description" content="Licensed plumber in Springfield.">'
            '<meta name="viewport" content="width=device-width">'
            '<link rel="canonical" href="https://www.acme-plumbing.example/">%s%s</head><body>%s</body></html>'
            % (head_extra, blocks, body))


def levels(result, level):
    return [f["message"] for f in result["findings"] if f["level"] == level]


URL = "https://www.acme-plumbing.example/"


class AuditTests(unittest.TestCase):
    def test_clean_page_has_no_errors_or_warnings(self):
        r = audit.analyze_html(page(), URL)
        self.assertEqual(levels(r, "error"), [])
        self.assertEqual(levels(r, "warning"), [])
        self.assertEqual(r["business_types"], ["Plumber"])

    def test_missing_schema_is_reported(self):
        r = audit.analyze_html(page(schema=None), URL)
        self.assertTrue(any("No LocalBusiness structured data" in m for m in levels(r, "warning")))

    def test_invalid_json_is_an_error(self):
        r = audit.analyze_html(page(schema='{"@type": "Plumber",}'), URL)
        self.assertTrue(any("not valid JSON" in m for m in levels(r, "error")))

    def test_required_properties(self):
        s = dict(GOOD_SCHEMA)
        del s["name"], s["address"]
        errors = levels(audit.analyze_html(page(s), URL), "error")
        self.assertTrue(any("`name`" in m for m in errors))
        self.assertTrue(any("`address`" in m for m in errors))

    def test_self_serving_reviews_warned(self):
        s = dict(GOOD_SCHEMA, aggregateRating={"@type": "AggregateRating", "ratingValue": 4.9, "reviewCount": 120})
        self.assertTrue(any("review stars" in m for m in levels(audit.analyze_html(page(s), URL), "warning")))

    def test_geo_precision(self):
        s = dict(GOOD_SCHEMA, geo={"@type": "GeoCoordinates", "latitude": 39.78, "longitude": -89.65})
        self.assertTrue(any("5 decimal places" in m for m in levels(audit.analyze_html(page(s), URL), "warning")))

    def test_bad_hours_values(self):
        s = dict(GOOD_SCHEMA, openingHoursSpecification={"dayOfWeek": "Funday", "opens": "9am", "closes": "17:00"})
        errors = levels(audit.analyze_html(page(s), URL), "error")
        self.assertTrue(any("dayOfWeek" in m for m in errors))
        self.assertTrue(any("`opens`" in m for m in errors))

    def test_schema_org_day_urls_are_accepted(self):
        s = dict(GOOD_SCHEMA, openingHoursSpecification={"dayOfWeek": "https://schema.org/Monday", "opens": "09:00:00", "closes": "17:00"})
        self.assertEqual(levels(audit.analyze_html(page(s), URL), "error"), [])

    def test_graph_documents_are_searched(self):
        doc = {"@context": "https://schema.org", "@graph": [{"@type": "WebSite", "name": "x"}, GOOD_SCHEMA]}
        self.assertEqual(audit.analyze_html(page(doc), URL)["business_types"], ["Plumber"])

    def test_phone_mismatch_and_hidden_address(self):
        body = '<h1>Plumber in Springfield</h1><p>Acme Plumbing</p><a href="tel:+15550109999">Call</a>'
        warnings = levels(audit.analyze_html(page(body=body), URL), "warning")
        self.assertTrue(any("does not match any click-to-call" in m for m in warnings))
        self.assertTrue(any("street address" in m for m in warnings))

    def test_noindex_is_an_error(self):
        r = audit.analyze_html(page(head_extra='<meta name="robots" content="noindex, follow">'), URL)
        self.assertTrue(any("noindex" in m for m in levels(r, "error")))

    def test_url_on_another_site(self):
        s = dict(GOOD_SCHEMA, url="https://www.facebook.com/acme")
        self.assertTrue(any("another site" in m for m in levels(audit.analyze_html(page(s), URL), "warning")))

    def test_www_and_bare_host_are_the_same_site(self):
        s = dict(GOOD_SCHEMA, url="https://acme-plumbing.example/")
        self.assertFalse(any("another site" in m for m in levels(audit.analyze_html(page(s), URL), "warning")))

    def test_cross_page_phone_conflict(self):
        other = dict(GOOD_SCHEMA, telephone="+1-555-010-7777")
        a = audit.analyze_html(page(), URL)
        b = audit.analyze_html(page(other), URL + "contact/")
        cross = audit.compare_sites([a, b])
        self.assertTrue(any("different phone numbers" in f["message"] for f in cross))

    def test_markdown_report_renders(self):
        md = audit.markdown([audit.analyze_html(page(), URL)], [])
        self.assertIn("# Local SEO audit", md)
        self.assertIn("0 errors", md)


if __name__ == "__main__":
    unittest.main()
