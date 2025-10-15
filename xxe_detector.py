import sys, re, os, argparse
from xml.etree.ElementTree import fromstring as safe_fromstring

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
            inds.append({"type": name, "match": m.group(0)})
    sev = "LOW"
    if any(i["type"] in ("FILE_URI","HTTP","HTTPS","SYSTEM","PUBLIC") for i in inds):
        sev = "HIGH"
    elif any(i["type"] in ("DOCTYPE","ENTITY","PARAM_ENTITY") for i in inds):
        sev = "MEDIUM"
    return {"severity": sev, "indicators": inds}

def safe_parse(text):
    try:
        root = safe_fromstring(text)
        return {"parsed": True, "root": getattr(root, "tag", None)}
    except Exception as e:
        return {"parsed": False, "error": str(e)}

def is_binary(path, n=1024):
    try:
        with open(path, 'rb') as f:
            return b'\0' in f.read(n)
    except Exception:
        return True

def scan_file(path):
    if is_binary(path):
        return {"file": path, "skipped": True, "reason": "binary"}
    try:
        with open(path, 'r', errors='ignore') as fh:
            txt = fh.read()
        if not txt.strip():
            return {"file": path, "skipped": True, "reason": "empty"}
        return {"file": path, "skipped": False, "scan": scan(txt), "parse": safe_parse(txt)}
    except Exception as e:
        return {"file": path, "skipped": True, "reason": str(e)}

def main(argv=None):
    p = argparse.ArgumentParser(description="Simple XXE detector")
    p.add_argument("-f","--file", help="File to scan (optional)")
    p.add_argument("--brief", action="store_true")
    args = p.parse_args(argv)

    targets = []
    if args.file and os.path.exists(args.file):
        targets = [args.file]
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
        for name in os.listdir(folder):
            fp = os.path.join(folder, name)
            if os.path.isfile(fp) and fp != os.path.abspath(__file__):
                if name.lower().endswith(('.xml','.html','.conf')):
                    targets.append(fp)

    if not targets:
        print("No .xml, .html, or .conf files found.", file=sys.stderr)
        sys.exit(3)

    high = False
    for t in sorted(targets):
        res = scan_file(t)
        print("="*60)
        print("File:", os.path.basename(t))
        if res.get("skipped"):
            print("Skipped:", res["reason"])
            continue
        s = res["scan"]
        print("Severity:", s["severity"])
        if s["indicators"]:
            for i in s["indicators"][:10]:
                print(" -", i["type"], "->", i["match"])
        else:
            print("No suspicious patterns found.")
        if s["severity"] == "HIGH":
            high = True

    sys.exit(1 if high else 0)

if __name__ == "__main__":
    main()
