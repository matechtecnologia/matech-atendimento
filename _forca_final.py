with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# CSS forçado no final do <head>
forca = '''
<style>
/* FORCA BOTAO IA - REGRA FINAL */
#ia-btn-header,
button#ia-btn-header,
.topo > #ia-btn-header {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: auto !important;
    min-width: 120px !important;
    height: auto !important;
    min-height: 36px !important;
    max-height: 60px !important;
    padding: 6px 14px !important;
    margin: 0 12px 0 0 !important;
    overflow: visible !important;
    position: relative !important;
    flex: 0 0 auto !important;
    align-self: center !important;
    box-sizing: border-box !important;
    color: #a78bfa !important;
    background: rgba(124, 58, 237, 0.1) !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
    border-radius: 100px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    z-index: 100 !important;
}
#ia-btn-header.on {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
    border-color: #a855f7 !important;
    color: #fff !important;
}
#ia-btn-header .btn-ia-icone {
    display: inline-block !important;
    width: auto !important;
    font-size: 14px !important;
    margin-right: 6px !important;
}
#ia-btn-header .btn-ia-txt {
    display: inline-block !important;
    width: auto !important;
    font-size: 11px !important;
    color: inherit !important;
}
#ia-btn-header .btn-ia-status {
    display: inline-flex !important;
    width: auto !important;
    font-size: 10px !important;
    margin-left: 8px !important;
    color: inherit !important;
}
</style>
'''

if "#ia-btn-header,\nbutton#ia-btn-header" not in c:
    c = c.replace("</head>", forca + "\n</head>", 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - CSS forcado no head")
else:
    print("AVISO - ja estava")
