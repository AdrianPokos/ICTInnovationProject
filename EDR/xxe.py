import sys, re, json, os, argparse

# try defusedxml for safety
try:
    from defusedxml.ElementTree import fromstring as safe_fromstring
    DEFUSED = True
except Exception:
    try:
        from xml.etree.ElementTree import fromstring as safe_fromstring
        DEFUSED = False
    except Exception:
        safe_fromstring = None
        DEFUSED = False

PATTERNS = [
    (r'<!DOCTYPE', "DOCTYPE"),
    (r'<!ENTITY', "ENTITY"),
    (r'SYSTEM\s+"[^"]+"', "SYSTEM"),
    (r'PUBLIC\s+"[^"]+"', "PUBLIC"),
    (r'%\w+\s*;', "PARAM_ENTITY"),
    (r'file://', "FILE_URI"),
    (r'http://', "HTTP"),
    (r'https://', "HTTPS"),
]

def scan(text):
    inds = []
    for p, name in PATTERNS:
        for m in re.finditer(p, text, re.I):
            inds.append({"type": name, "match": m.group(0), "pos": m.start()})
    sev = "LOW"
    if any(i["type"] in ("FILE_URI","HTTP","HTTPS","SYSTEM","PUBLIC") for i in inds):
        sev = "HIGH"
    elif any(i["type"] in ("DOCTYPE","ENTITY","PARAM_ENTITY") for i in inds):
        sev = "MEDIUM"
    return {"severity": sev, "indicators": inds, "length": len(text)}

def safe_parse(text):
    if safe_fromstring is None:
        return {"parsed": False, "error": "No parser available"}
    try:
        root = safe_fromstring(text)
        return {"parsed": True, "root": getattr(root, "tag", None), "using_defused": DEFUSED}
    except Exception as e:
        return {"parsed": False, "error": str(e)}

def mainxxe(argv=None):
    p = argparse.ArgumentParser(description="Simple XXE detector")
    p.add_argument("-f","--file", help="XML file")
    p.add_argument("--json", help="Write JSON report")
    p.add_argument("--brief", action="store_true")
    args = p.parse_args(argv)

    if args.file:
        if not os.path.exists(args.file):
            print("File not found", file=sys.stderr); sys.exit(2)
        with open(args.file, 'r', errors='ignore') as fh:
            txt = fh.read()
    else:
        if sys.stdin.isatty():
            print("Paste XML then EOF:", file=sys.stderr)
        txt = sys.stdin.read()

    if not txt:
        print("No input", file=sys.stderr); sys.exit(3)

    report = {"scan": scan(txt), "parse": safe_parse(txt)}
    if not args.brief:
        print("Severity:", report["scan"]["severity"])
        print("Indicators:", len(report["scan"]["indicators"]))
        for i in report["scan"]["indicators"][:10]:
            print(" -", i["type"], "->", i["match"])
        if report["parse"]["parsed"]:
            print("Parsed root:", report["parse"]["root"])
            print("Used defusedxml:", report["parse"]["using_defused"])
        else:
            print("Parse error:", report["parse"].get("error"))
    if args.json:
        try:
            with open(args.json, 'w') as jf:
                json.dump(report, jf, indent=2)
            print("Wrote", args.json)
        except Exception as e:
            print("JSON write failed:", e, file=sys.stderr)
    sys.exit(1 if report["scan"]["severity"]=="HIGH" else 0)

if __name__ == "__main__":
    mainxxe()