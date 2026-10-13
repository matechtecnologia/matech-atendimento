with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Troca a media query por uma versao que garante o botao aparecer
antigo = '''        @media (max-width: 600px) {
            .topo {
                padding: 10px 12px !important;
                flex-wrap: wrap;
                gap: 8px;
            }
            .topo h1 {
                font-size: 14px !important;
            }
            .usuario-info {
                gap: 6px !important;
                font-size: 11px !important;
                flex-wrap: wrap;
            }
            .usuario-nome {
                display: none;
            }
            .btn-ia {
                padding: 5px 10px 5px 8px;
                margin-right: 0;
                gap: 6px;
            }
            .btn-ia-icone { font-size: 12px; }
            .btn-ia-txt { font-size: 10px; }
            .btn-ia-status {
                font-size: 8px;
                padding: 2px 6px;
                gap: 3px;
            }
            .btn-ia-status .dot {
                width: 4px;
                height: 4px;
            }
        }'''

novo = '''        @media (max-width: 768px) {
            .topo {
                padding: 10px 12px !important;
                flex-wrap: wrap;
                gap: 8px;
            }
            .topo h1 {
                font-size: 14px !important;
                flex: 0 0 auto;
            }
            .usuario-info {
                gap: 6px !important;
                font-size: 11px !important;
                flex-wrap: wrap;
                flex: 1 1 auto;
                justify-content: flex-end;
            }
            .usuario-nome {
                display: none;
            }
            .btn-ia {
                display: inline-flex !important;
                padding: 5px 10px 5px 8px !important;
                margin-right: 0 !important;
                gap: 6px !important;
                flex-shrink: 0;
            }
            .btn-ia-icone { font-size: 12px !important; }
            .btn-ia-txt { font-size: 10px !important; }
            .btn-ia-status {
                font-size: 8px !important;
                padding: 2px 6px !important;
                gap: 3px !important;
            }
            .btn-ia-status .dot {
                width: 4px !important;
                height: 4px !important;
            }
        }
        @media (max-width: 480px) {
            .btn-ia-txt { display: none !important; }
            .btn-ia { padding: 6px 10px !important; }
        }'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - media query melhorada")
else:
    print("AVISO - media antiga nao achada")
