#!/usr/bin/env python3
"""Shampoo Ingredient Ontology v5.0 — Consumer Web Interface.

Serves a single-page HTML application at localhost:8000 using Python's
http.server (standard library only).

Run: python3 shampoo_ontology_server.py
Open: http://localhost:8000
"""

import http.server
import json
import os
import sys
import threading
import urllib.parse

from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_V4_PATH = str(_PROJECT_ROOT / "shampoo-ontology-v4")
if _V4_PATH not in sys.path:
    sys.path.insert(0, _V4_PATH)

import shampoo_ontology_parser as m1
import shampoo_ontology_divergence as m2
import shampoo_ontology_fragrance as m3
import shampoo_ontology_supplier_audit as m4

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Shampoo Ingredient Ontology v5.0</title>
<style>
body{margin:0;padding:20px;background:#faf8f5;color:#1a1a1a;font-family:Georgia,"Times New Roman",serif;line-height:1.55}
.container{max-width:1100px;margin:0 auto;background:#fff;padding:32px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
h1,h2,h3{color:#1e3a5f;font-weight:normal}
h1{border-bottom:3px solid #c41e3a;padding-bottom:12px}
textarea{width:100%;height:120px;font-family:monospace;font-size:14px;padding:12px;border:1px solid #d8d3cc;resize:vertical;box-sizing:border-box}
select,input[type=text]{padding:8px;border:1px solid #d8d3cc;font-family:Georgia,serif;font-size:14px;box-sizing:border-box}
button{padding:10px 24px;background:#1e3a5f;color:#fff;border:none;cursor:pointer;font-size:14px;font-family:Georgia,serif}
button:hover{background:#c41e3a}
.section{margin:24px 0;padding:16px;border-left:4px solid #1e3a5f;background:#faf8f5}
.dusting{color:#c41e3a;font-weight:bold}
.preservative{color:#e67e22}
.allergen{color:#c41e3a}
.safe{color:#2d6a4f}
.flag-bar{display:flex;gap:8px;margin:12px 0;flex-wrap:wrap}
.flag-item{padding:4px 12px;border-radius:4px;font-size:13px;color:#fff}
.flag-dusting{background:#c41e3a}
.flag-preservative{background:#e67e22}
.flag-allergen{background:#c41e3a}
.flag-safe{background:#2d6a4f}
table{width:100%;border-collapse:collapse;margin:12px 0}
th,td{border:1px solid #d8d3cc;padding:8px;text-align:left;font-size:14px}
th{background:#1e3a5f;color:#fff}
.status-pass{color:#2d6a4f;font-weight:bold}
.status-fail{color:#c41e3a;font-weight:bold}
.status-warn{color:#e67e22;font-weight:bold}
@media(max-width:768px){.container{padding:18px}}
</style>
</head>
<body>
<div class="container">
<h1>Shampoo Ingredient Ontology <span style="color:#c41e3a">v5.0</span></h1>
<p style="color:#1e3a5f">Paste a shampoo ingredient list and click Analyze.</p>
<div class="section">
<h3>Ingredient Input</h3>
<textarea id="ingredients" placeholder="Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine..."></textarea><br><br>
<label>Product Category:</label>
<select id="category">
<option value="mass_market">Mass Market</option>
<option value="premium">Premium</option>
<option value="anti_dandruff">Anti-Dandruff</option>
<option value="natural">Natural</option>
<option value="baby">Baby</option>
<option value="mens">Men's</option>
<option value="professional">Professional</option>
</select><br><br>
<label>Product Name:</label>
<select id="product_name">
<option value="Pantene Pro-V Daily Moisture Renewal">Pantene Pro-V</option>
<option value="Head &amp; Shoulders Classic Clean">Head &amp; Shoulders</option>
<option value="Dove Daily Moisture Shampoo">Dove</option>
<option value="Herbal Essences Bio:renew">Herbal Essences</option>
<option value="L'Oreal Elvive Total Repair 5">L'Oreal Elvive</option>
<option value="Garnier Fructis Grow Strong">Garnier Fructis</option>
<option value="Aussie Miracle Moist">Aussie</option>
<option value="TRESemme Keratin Smooth">TRESemme</option>
<option value="Sunsilk Co-Creations">Sunsilk</option>
<option value="Clear Complete Soft Care">Clear</option>
</select><br><br>
<label>Supplier Codes (comma-separated):</label>
<input type="text" id="supplier_codes" placeholder="BASF_TEXAPON_N70,BASF_DEHYTON_PK45" style="width:100%"><br><br>
<label>Brand Claims (comma-separated):</label>
<input type="text" id="brand_claims" placeholder="paraben-free,natural" style="width:100%"><br><br>
<button onclick="analyze()">Analyze</button>
</div>
<div id="results"></div>
</div>
<script>
async function analyze(){var ing=document.getElementById("ingredients").value;var cat=document.getElementById("category").value;var prod=document.getElementById("product_name").value;var supp=document.getElementById("supplier_codes").value;var claims=document.getElementById("brand_claims").value;var body="ingredients="+encodeURIComponent(ing)+"&category="+encodeURIComponent(cat)+"&product_name="+encodeURIComponent(prod)+"&supplier_codes="+encodeURIComponent(supp)+"&brand_claims="+encodeURIComponent(claims);var resp=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:body});var data=await resp.json();render(data);}
function render(d){var h="";if(d.error){h+='<div class="section"><p class="dusting">Error: '+d.error+"</p></div>";document.getElementById("results").innerHTML=h;return;}var p=d.parser||{};var div=d.divergence||{};var frag=d.fragrance||{};var audit=d.supplier_audit||{};var summary=d.summary||{};h+='<h2>Analysis Results</h2>';h+='<div class="flag-bar">';if(summary.dusting_risk_count>0)h+='<span class="flag-item flag-dusting">'+summary.dusting_risk_count+' Dusting</span>';if(summary.preservative_count>0)h+='<span class="flag-item flag-preservative">'+summary.preservative_count+' Preservatives</span>';if(summary.allergen_count>0)h+='<span class="flag-item flag-allergen">'+summary.allergen_count+' Allergens</span>';if(summary.claim_violations>0)h+='<span class="flag-item flag-preservative">'+summary.claim_violations+' Claim Violations</span>';h+='</div>';h+='<h3>Ingredient Breakdown</h3><table><tr><th>Ingredient</th><th>Est. %</th><th>Flags</th></tr>';var above=p.above_threshold||[];var below=p.below_threshold||[];var all=above.concat(below);var dusting_names=(p.dusting_confirmed||[]).map(function(x){return x.name});var preservative_names=(p.preservatives_flagged_list||[]).map(function(x){return x.name});var allergen_names=(p.fragrance_allergens_list||[]).map(function(x){return x.name});for(var i=0;i<all.length;i++){var ing=all[i];var cls="safe";var flags=[];if(dusting_names.indexOf(ing.name)>=0){cls="dusting";flags.push("DUSTING")}if(preservative_names.indexOf(ing.name)>=0){cls="preservative";flags.push("PRESERVATIVE")}if(allergen_names.indexOf(ing.name)>=0){cls="allergen";flags.push("ALLERGEN")}h+='<tr><td class="'+cls+'">'+ing.name+'</td><td>'+ing.estimated_pct+'</td><td>'+flags.join(", ")+'</td></tr>'}h+="</table>";if(div.us_regulated){h+='<div class="section"><h3>Jurisdiction Comparison</h3><table><tr><th>Jurisdiction</th><th>Regulated Substances</th></tr>';h+='<tr><td>US</td><td>'+(div.us_regulated||[]).join(", ")+'</td></tr>';h+='<tr><td>EU</td><td>'+(div.eu_regulated||[]).join(", ")+'</td></tr>';h+='<tr><td>JP</td><td>'+(div.jp_regulated||[]).join(", ")+'</td></tr>';h+='<tr><td>CN</td><td>'+(div.cn_regulated||[]).join(", ")+'</td></tr>';h+="</table></div>"}if(frag.category){h+='<div class="section"><h3>Fragrance Analysis</h3>';h+='<p>Category: '+frag.category+' | Compounds: '+frag.estimated_compounds+' | IFRA: '+frag.ifra_coverage_pct+'%</p>';h+='<p>Top: '+frag.top_notes_count+' | Mid: '+frag.middle_notes_count+' | Base: '+frag.base_notes_count+' | Hidden: '+frag.hidden_non_disclosed+'</p>';h+="</div>"}if(audit.claim_verification){h+='<div class="section"><h3>Supplier Audit</h3><table><tr><th>Claim</th><th>Status</th><th>Evidence</th></tr>';var cv=audit.claim_verification||[];for(var j=0;j<cv.length;j++){var c=cv[j];var st=c.status=="TRUE"?"status-pass":(c.status=="FALSE"?"status-fail":"status-warn");h+='<tr><td>'+c.claim+'</td><td class="'+st+'">'+c.status+'</td><td>'+c.evidence+'</td></tr>'}h+="</table></div>"}document.getElementById("results").innerHTML=h;}
document.getElementById("ingredients").value="Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, Sodium Chloride, Glycol Distearate, Dimethicone, Fragrance, Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, Panthenol, Panthenyl Ethyl Ether, Methylchloroisothiazolinone, Methylisothiazolinone, Argania Spinosa Kernel Oil, Histidine";
</script>
</body>
</html>"""


class ShampooHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the shampoo ontology web interface.

    Serves HTML on GET /, processes analysis on POST /analyze.
    Enforces input size limits and uses a threading lock.
    """

    _lock = threading.Lock()
    MAX_INPUT_LENGTH = 10000
    MAX_INGREDIENTS = 200
    _DANGEROUS = ("<script", "javascript:", "onerror=", "onload=",
                   "<iframe", "<img ", "data:text/html", "<?php")

    def do_GET(self):
        """Serve the main HTML page at ``/``."""
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST /analyze — parse and return JSON analysis."""
        if self.path != "/analyze":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(body)

        raw = params.get("ingredients", [""])[0]
        category = params.get("category", ["mass_market"])[0]

        # --- Input validation ---
        if not raw or not raw.strip():
            self._send_error("Empty input — please paste an ingredient list.")
            return
        if len(raw) > self.MAX_INPUT_LENGTH:
            self._send_error(f"Input exceeds {self.MAX_INPUT_LENGTH} chars (got {len(raw)}).")
            return
        for pat in self._DANGEROUS:
            if pat.lower() in raw.lower():
                self._send_error("Input contains a prohibited pattern.")
                return
        tokens = [t.strip() for t in raw.replace("\n", ",").replace(";", ",").split(",") if t.strip()]
        if len(tokens) > self.MAX_INGREDIENTS:
            self._send_error(f"Too many ingredients ({len(tokens)} > {self.MAX_INGREDIENTS}).")
            return

        product_name = params.get("product_name", [""])[0]
        supplier_codes_raw = params.get("supplier_codes", [""])[0]
        brand_claims_raw = params.get("brand_claims", [""])[0]
        supplier_codes = [c.strip() for c in supplier_codes_raw.split(",") if c.strip()]
        brand_claims = [c.strip() for c in brand_claims_raw.split(",") if c.strip()]

        try:
            with ShampooHandler._lock:
                # Parser
                parser = m1.IngredientListParser()
                parse_result = parser.parse(raw)

                # Divergence
                tracker = m2.DivergenceTracker()
                divergence_result = {}
                if product_name:
                    divergence_result = tracker.compare_jurisdictions(product_name)

                # Fragrance
                engine = m3.FragranceEngine(product_category=category)
                normalized = parse_result.get("input_normalized", [])
                disclosed = []
                if hasattr(m3, "EU_ALLERGENS"):
                    for aller in m3.EU_ALLERGENS:
                        if any(aller.upper() == i.upper() for i in normalized):
                            disclosed.append(aller)
                engine.set_disclosed_allergens(disclosed)
                engine.compute_probabilities()
                engine.classify_notes()
                engine.identify_hidden_non_disclosed()
                fragrance_result = engine.generate_report()

                # Supplier audit
                audit = m4.SupplierAudit(
                    product_name=product_name or "Unknown Product",
                    ingredient_list=normalized,
                    supplier_codes=supplier_codes,
                    brand_claims=brand_claims,
                )
                supplier_result = audit.audit()

                # Summary
                summary = {
                    "total_ingredients": len(normalized),
                    "dusting_risk_count": len(parse_result.get("dusting_confirmed", [])),
                    "preservative_count": len(parse_result.get("preservatives_flagged", [])),
                    "allergen_count": len(parse_result.get("fragrance_allergens", [])),
                    "supplier_flag_count": sum(
                        len(p.get("flags", []))
                        for p in supplier_result.get("preservatives_from_carryover", [])
                    ),
                    "claim_violations": sum(
                        1 for c in supplier_result.get("claim_verification", [])
                        if c.get("status") in ("FALSE", "WARNING")
                    ),
                }

                response = {
                    "parser": {
                        "above_threshold": parse_result.get("above_threshold", []),
                        "below_threshold": parse_result.get("below_threshold", []),
                        "dusting_confirmed": parse_result.get("dusting_confirmed", []),
                        "preservatives_flagged_list": parse_result.get("preservatives_flagged", []),
                        "fragrance_allergens_list": parse_result.get("fragrance_allergens", []),
                    },
                    "divergence": {
                        "us_regulated": divergence_result.get("jurisdictions", {}).get("US", {}).get("regulated_found", []),
                        "eu_regulated": divergence_result.get("jurisdictions", {}).get("EU", {}).get("regulated_found", []),
                        "jp_regulated": divergence_result.get("jurisdictions", {}).get("JP", {}).get("regulated_found", []),
                        "cn_regulated": divergence_result.get("jurisdictions", {}).get("CN", {}).get("regulated_found", []),
                    },
                    "fragrance": {
                        "category": fragrance_result.get("product_category", ""),
                        "estimated_compounds": fragrance_result.get("estimated_compound_count", 0),
                        "top_notes_count": len(fragrance_result.get("top_notes", [])),
                        "middle_notes_count": len(fragrance_result.get("middle_notes", [])),
                        "base_notes_count": len(fragrance_result.get("base_notes", [])),
                        "hidden_non_disclosed": len(fragrance_result.get("hidden_non_disclosed", [])),
                        "ifra_coverage_pct": fragrance_result.get("ifra_coverage_pct", 0),
                    },
                    "supplier_audit": {
                        "claim_verification": supplier_result.get("claim_verification", []),
                        "regulatory_flags": supplier_result.get("regulatory_flags", []),
                    },
                    "summary": summary,
                }
        except Exception as e:
            response = {"error": str(e)}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response, default=str).encode("utf-8"))

    def _send_error(self, message):
        """Send a 400 JSON error response."""
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start the HTTP server on localhost:8000."""
    port = 8000
    server = http.server.HTTPServer(("localhost", port), ShampooHandler)
    print(f"Shampoo Ingredient Ontology v5.0 Server")
    print(f"Open http://localhost:{port} in your browser")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
