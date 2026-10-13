with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona CSS com !important pra forcar visibilidade
novo_css = '''
        /* FORCAR BOTAO IA APARECER */
        .topo .btn-ia {
            display: inline-flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            align-items: center;
            gap: 8px;
            padding: 6px 12px 6px 10px;
            background: rgba(124, 58, 237, 0.08);
            border: 1px solid rgba(124, 58, 237, 0.25);
            border-radius: 100px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.25s;
            margin-right: 12px;
        }
        .topo .usuario-info {
            display: flex !important;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }
'''

# Adiciona antes do </style>
c = c.replace("    </style>\n</head>", novo_css + "    </style>\n</head>", 1)

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - CSS forcado")
