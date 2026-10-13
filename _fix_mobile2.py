with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona CSS extra pra forcar botao no mobile
extra_css = '''
        /* FORCAR BOTAO MOBILE - REGRA FINAL */
        @media (max-width: 768px) {
            body .topo .usuario-info .btn-ia,
            body .topo .btn-ia,
            .btn-ia#ia-btn-header {
                display: inline-flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                position: static !important;
                width: auto !important;
                height: auto !important;
                overflow: visible !important;
                transform: none !important;
            }
        }
'''

# Insere antes do ultimo </style>
idx = c.rfind("</style>")
if idx != -1:
    c = c[:idx] + extra_css + "\n    " + c[idx:]
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - CSS final adicionado")
else:
    print("ERRO - nao achou </style>")
