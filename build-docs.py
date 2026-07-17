#!/usr/bin/env python3
"""Render the markdown docs into styled, self-contained HTML pages for the website."""
import markdown, re, html as _html

CSS = """
:root{--b600:#7A47E8;--b700:#6538CE;--b50:#F7F4FE;--b100:#EFE8FC;--b200:#DCCEF9;
--ink:#101828;--ink2:#344054;--ink3:#667085;--line:#E4E7EC;--bg:#F9FAFB}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink2);
font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}
.top{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.86);backdrop-filter:blur(8px);
border-bottom:1px solid var(--line);padding:12px 24px;display:flex;align-items:center;gap:12px}
.top a.back{color:var(--ink3);text-decoration:none;font-size:14px;font-weight:600}
.top a.back:hover{color:var(--b700)}
.logo{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:17px;letter-spacing:-.02em;color:var(--ink)}
.logo .lg{width:26px;height:26px;border-radius:7px;background:var(--b600);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:13px}
.wrap{max-width:820px;margin:0 auto;padding:44px 24px 96px}
h1{font-size:34px;line-height:1.2;letter-spacing:-.025em;color:var(--ink);margin:0 0 6px}
h1+p{font-size:15px;color:var(--ink3);margin-top:0}
h2{font-size:23px;letter-spacing:-.02em;color:var(--ink);margin:44px 0 12px;padding-top:14px;border-top:1px solid var(--line)}
h3{font-size:17px;letter-spacing:-.01em;color:var(--ink);margin:26px 0 6px}
p{margin:0 0 15px}
strong{color:var(--ink);font-weight:650}
a{color:var(--b700)}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin:5px 0}
hr{border:none;border-top:1px solid var(--line);margin:30px 0}
code{background:var(--b50);border:1px solid var(--b100);border-radius:5px;padding:1px 6px;font-size:13.5px;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--b700)}
table{width:100%;border-collapse:collapse;margin:8px 0 22px;font-size:14.5px;background:#fff;
border:1px solid var(--line);border-radius:12px;overflow:hidden}
th{text-align:left;background:var(--b50);color:var(--ink);font-weight:650;font-size:13px;
text-transform:uppercase;letter-spacing:.03em;padding:11px 16px;border-bottom:1px solid var(--line)}
td{padding:12px 16px;border-bottom:1px solid #F2F4F7;vertical-align:top}
tr:last-child td{border-bottom:none}
td strong{color:var(--b700)}
blockquote{margin:0 0 15px;padding:2px 18px;border-left:3px solid var(--b200);color:var(--ink3)}
.toc{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin:26px 0 8px}
.toc .t{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--ink3);margin-bottom:8px}
.toc ul{margin:0;padding-left:18px}
.toc li{margin:3px 0}
.toc a{text-decoration:none;color:var(--ink2);font-size:14.5px}
.toc a:hover{color:var(--b700)}
.foot{margin-top:52px;padding-top:20px;border-top:1px solid var(--line);color:#98A2B3;font-size:13px}
@media(max-width:640px){.wrap{padding:28px 18px 72px}h1{font-size:27px}h2{font-size:20px}}
"""

def build(md_path, out_path, title):
    text = open(md_path).read()
    md = markdown.Markdown(extensions=['tables','fenced_code','toc','attr_list'],
                           extension_configs={'toc':{'toc_depth':'2-2','permalink':False}})
    body = md.convert(text)
    toc_items = getattr(md, 'toc_tokens', [])
    toc = ''
    if toc_items:
        links = ''.join(f'<li><a href="#{t["id"]}">{_html.escape(t["name"])}</a></li>' for t in toc_items)
        toc = f'<nav class="toc"><div class="t">Contents</div><ul>{links}</ul></nav>'
    # inject TOC right after the h1 + subtitle block (after first </p>)
    m = re.search(r'</p>', body)
    if m and toc:
        i = m.end()
        body = body[:i] + toc + body[i:]
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Finmo Door 1</title>
<style>{CSS}</style></head>
<body>
<div class="top"><span class="logo"><span class="lg">f</span>finmo</span>
<a class="back" href="./index.html">&larr; Back to overview</a></div>
<main class="wrap">{body}
<div class="foot">Finmo Door 1 prototype · Siddharth Karmarkar. Prototype only; all data is illustrative.</div>
</main></body></html>"""
    open(out_path,'w').write(page)
    print('wrote', out_path)

build('DESIGN_DECISIONS.md','design-decisions.html','Design decisions')
build('PROD_IMPLEMENTATION.md','production.html','Production implementation')
