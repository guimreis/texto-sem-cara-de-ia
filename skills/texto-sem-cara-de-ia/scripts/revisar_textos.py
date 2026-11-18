#!/usr/bin/env python3
"""
Detector de estruturas sintaticas que denunciam texto gerado por IA.

O problema nunca esta no vocabulario: esta em ESTRUTURAS que se repetem. Um
padrao usado uma vez e retorica. O mesmo padrao cinco vezes na mesma pagina e
assinatura de maquina. Por isso o detector conta e pontua em vez de proibir.

Uso:
    revisar_textos.py CAMINHO [CAMINHO ...]     arquivos ou diretorios
    revisar_textos.py --texto "a mensagem"      um texto direto, sem arquivo
    revisar_textos.py . --ext md,html           extensoes (padrao: md,html,txt)
    revisar_textos.py . --min 3                 so o que tem 3+ achados
    revisar_textos.py . --peso 3                so os achados de peso 3
    revisar_textos.py . --md relatorio.md       grava relatorio em markdown
    revisar_textos.py . --json                  saida JSON, para script
    revisar_textos.py . --regras minhas.json    suas proprias regras (veja minhas-regras.json)

Sem --regras, ele usa o minhas-regras.json da pasta da skill, se existir.

Confere tambem fonte: afirmacao com numero, lei ou resolucao sem link nem
atribuicao na mesma frase ou na vizinha aparece como 'Afirmacao verificavel sem fonte'.

Le texto, HTML e Markdown. Em HTML, ignora header, footer, nav e menu, porque um
achado de menu apareceria em todas as paginas do site. Ignora tambem blocos de
FAQ (details/summary), onde pergunta seguida de resposta e o formato correto.
"""

import argparse
import html as _html
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# Padroes. Cada um: (id, titulo, peso, regex, saida sugerida)
#
# Peso 3 quase sempre soa automatico. Peso 2 e suspeito quando repete. Peso 1
# so incomoda por densidade.
# --------------------------------------------------------------------------
PADROES = [
    ("antitese-negada", "Antitese negada", 3,
     r"\bn[ãa]o\s+\w+[^.!?;]{0,90}?,\s*(?:é|e)\s+\w|"
     r"\bn[ãa]o\s+(come[çc]\w+|é|e|foi|se\s+trata)\b[^.!?]{0,70}\.\s*\1",
     "Afirme o Y direto. O leitor nao precisa do X que voce descartou."),

    ("antitese-invertida", "Antitese invertida (X, nao Y)", 3,
     r"(?i)[\wÀ-ú\)\]\"]\s*,\s+n[ãa]o\s+(?:o\s+|a\s+|os\s+|as\s+|um\s+|uma\s+|de\s+|para\s+|em\s+)?\w",
     "Fique so com a afirmacao. A metade negativa e enfeite."),

    ("ausencia-retorica", "Ausencia retorica", 3,
     r"(?i)\bn[ãa]o\s+[ée]\s+(?:a\s+)?(?:falta|aus[êe]ncia|escassez)\s+de\b[^.!?;]{0,80}?,\s*[ée]\b",
     "Diga o que falta, uma vez."),

    ("negacao-tripla", "Negacao tripla", 3,
     r"(?i)\bsem\s+[^,.;!?]{2,40},\s*sem\s+[^,.;!?]{2,40},\s*sem\s+",
     "Escolha a negacao que importa, ou diga no positivo."),

    ("nao-apenas-mas", "\"nao apenas X, mas Y\"", 3,
     r"(?i)\bn[ãa]o\s+(?:(?:[ée]|foi|s[ãa]o|est[áa]|fica)\s+)?(?:apenas|s[óo]|somente)\b[^.!?;]{0,80}?,?\s*(?:mas|[ée])\b",
     "Fique com o item mais forte."),

    ("aforismo-divida", "Aforismo de fechamento", 3,
     r"(?i)\b[ée]\s+(?:d[íi]vida\s+t[ée]cnica|uma\s+bomba|um\s+cheque|conta\s+que\s+chega)\b[^.!?]{0,40}",
     "Termine no fato. O aforismo enfraquece o que veio antes."),

    ("transformacao-ritual", "Transformacao ritual", 2,
     r"(?i)\bdeixa\s+de\s+ser\b[^.!?;]{0,60}?\be\s+passa\s+a\s+ser\b",
     "Descreva o estado final."),

    ("conector-e-aqui-que", "Conector \"E aqui que\" / \"E por isso que\"", 2,
     r"(?:^|[.!?]\s+|>\s*)[ÉE]\s+(?:aqui|por\s+isso|assim)\s+que\b",
     "Comece pela informacao."),

    ("triplete-nominal", "Triplete nominal", 2,
     r"(?i)\bum(?:a)?\s+\w+,\s+um(?:a)?\s+\w+,\s+um(?:a)?\s+\w+",
     "Dois itens, ou uma frase com verbo."),

    ("paralelismo-cada", "Paralelismo mecanico com \"cada\"", 2,
     r"\b[Cc]ada\s+\w+[^.!?;]{0,60}?,\s*e\s+cada\s+\w+",
     "Corte o segundo elo. O primeiro ja fez o ponto."),

    ("titulo-palavras-frase", "Titulo de palavras-frase", 2,
     r"(?:^|\n)#{0,6}\s*\**[A-ZÀ-Ú][\wÀ-ú]+\.\s+[A-ZÀ-Ú][\wÀ-ú]+\.\s+[A-ZÀ-Ú][\wÀ-ú]+\.",
     "Uma frase com sujeito e verbo diz mais."),

    ("pergunta-autorrespondida", "Pergunta retorica autorrespondida", 2,
     r"\?\s+(?:[OoAa]\s+\w+|Ele|Ela|Isso|Porque|Por\s+que)\b[^.!?]{0,60}[.!]",
     "Corte a pergunta e deixe a resposta."),

    ("muleta-vira", "Muleta \"vira\"", 1,
     r"\bvir(?:a|am|ou|aram)\b(?!\s+(?:a\s+)?(?:esquina|p[áa]gina|noite|mesa))",
     "Use o verbo especifico."),

    ("em-vez-de", "\"em vez de\" recorrente", 1,
     r"\bem\s+vez\s+de\b",
     "Afirme o que e feito e deixe o contraponto de fora."),
]

# Palavras que nao existem em portugues sem acento. Ficam de fora de proposito as
# que tem homografo valido ("esta", "e", "as", "para", "ate"), senao a regra
# acusaria frase correta.
RE_ACENTO_FALTANDO = (
    r"(?i)\b(?:voce|nao|razao|padrao|amanha|reuniao|abraco|entao|tambem|sao|tres|"
    r"informacao|identificacao|validacao|criacao|atencao|referencia|concessionaria|"
    r"proximo|proxima|ultimo|ultima|apos|duvida|codigo|numero|pagina|familia|orgao|"
    r"servico|negocio|usuario|relatorio|escritorio|calculo|minimo|maximo|especifico|"
    r"tecnico|pratico|publico|historico|automatico|ja)\b"
)

# Regras de estilo que nao sao sintaxe, mas entram na mesma revisao.
ESTILO = [
    ("acento-faltando", "Palavra sem acento", 3,
     RE_ACENTO_FALTANDO,
     "Escreva a palavra acentuada."),
    ("travessao-espacado", "Travessao cercado de espacos", 2,
     r"\s[\u2014\u2013]\s",
     "Reescreva a frase sem o travessao."),
]

TODOS = PADROES + ESTILO

# Fonte. Afirmacao que alguem vai checar - numero com %, valor em R$, ano, lei, resolucao,
# ato, decreto, portaria - sem fonte na mesma frase ou na seguinte. Fonte aqui e link
# (http, ou [link], que e o que sobra de um <a href> depois da limpeza) ou a atribuicao
# escrita: "segundo", "conforme", "de acordo com", "fonte", "referencia".

FONTE_ID = "afirmacao-sem-fonte"
FONTE_TITULO = "Afirmacao verificavel sem fonte"
FONTE_PESO = 2
FONTE_SAIDA = ("Abra a fonte e confira o numero agora. Se houver pagina oficial, linke para "
               "ela na propria frase. Se nao abre ou nao diz isso, a frase sai ou vira 'segundo X'.")
RE_VERIFICAVEL = re.compile(
    r"\d+(?:[.,]\d+)?\s?%|R\$\s?\d|\bn[ºo°]\s?\d|"
    r"\b(?:Lei(?:\s+Complementar)?|LC|Resolu[çc][ãa]o|Ato\s+Conjunto|Decreto|Portaria|"
    r"Instru[çc][ãa]o\s+Normativa|Medida\s+Provis[óo]ria|Emenda\s+Constitucional)\b")
RE_FONTE = re.compile(
    r"(?i)https?://|\[link\]|\bsegundo\b|\bconforme\b|\bde\s+acordo\s+com\b|\bfonte\b|"
    r"\brefer[êe]ncias?\b|\baccording\s+to\b|\bsource\b|\bseg[úu]n\b")
RE_FRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ú0-9\[])")


def afirmacoes_sem_fonte(texto):
    """Frases com afirmacao verificavel e sem fonte nela nem na seguinte."""
    frases = [f.strip() for f in RE_FRASE.split(texto) if f.strip()]
    saida = []
    for i, frase in enumerate(frases):
        if not RE_VERIFICAVEL.search(frase):
            continue
        # a fonte pode estar na frase, na seguinte, ou na anterior (lista de referencias)
        anterior = frases[i - 1] if i > 0 else ""
        vizinha = frases[i + 1] if i + 1 < len(frases) else ""
        if RE_FONTE.search(frase) or RE_FONTE.search(vizinha) or RE_FONTE.search(anterior):
            continue
        saida.append({
            "id": FONTE_ID, "padrao": FONTE_TITULO, "peso": FONTE_PESO,
            "trecho": " ".join(frase.split())[:180], "saida": FONTE_SAIDA,
        })
    return saida

BLOCOS_IGNORADOS = re.compile(
    r"<(header|footer|nav|script|style|details)\b.*?</\1>|"
    r"<div[^>]*class=\"[^\"]*(mega-menu|topbar|site-header|site-footer|faq)[^\"]*\".*?</div>",
    re.S | re.I,
)

# Bloco declarado como pergunta e resposta POR DESENHO (class="pergunta-resposta"). A
# isencao vale SO para o padrao da pergunta autorrespondida: dentro dele a antitese
# negada e as outras continuam sendo defeito, e continuam aparecendo. Isentar o bloco
# inteiro abriria um ponto cego do tamanho do titulo.
BLOCO_PERGUNTA_RESPOSTA = re.compile(
    r"<div[^>]*class=\"[^\"]*pergunta-resposta[^\"]*\".*?</div>", re.S | re.I
)


def extrai_texto(caminho):
    """Texto limpo de um arquivo, em duas versoes.

    A primeira e o texto todo, sem chrome e sem FAQ, e e nela que quase tudo e procurado.
    A segunda tira tambem os blocos `pergunta-resposta`, e serve so ao padrao da pergunta
    autorrespondida. Em markdown as duas sao iguais.
    """
    with open(caminho, encoding="utf-8", errors="ignore") as fh:
        bruto = fh.read()

    if caminho.lower().endswith((".html", ".htm", ".page")):
        bruto = BLOCOS_IGNORADOS.sub(" ", bruto)
        # o link some quando as tags saem; fica um marcador para a regra de fonte enxergar
        bruto = re.sub(r'<a\b[^>]*href="https?://[^"]*"[^>]*>', " [link] ", bruto, flags=re.I)
        sem_pr = BLOCO_PERGUNTA_RESPOSTA.sub(" ", bruto)
        limpa = lambda t: re.sub(r"[ \t]+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", t)))
        return limpa(bruto), limpa(sem_pr)

    bruto = re.sub(r"```.*?```", " ", bruto, flags=re.S)
    bruto = re.sub(r"`[^`]+`", " ", bruto)
    bruto = re.sub(r"[ \t]+", " ", bruto)
    return bruto, bruto


ACENTOS = re.compile(r"[\u00e1\u00e0\u00e2\u00e3\u00e9\u00ea\u00ed\u00f3\u00f4\u00f5\u00fa\u00fc\u00e7"
                     r"\u00c1\u00c0\u00c2\u00c3\u00c9\u00ca\u00cd\u00d3\u00d4\u00d5\u00da\u00c7]")


def cobra_acento(texto):
    """So cobra acento de texto que JA acentua de forma consistente.

    Documento escrito de proposito sem acento (muita gente escreve assim no
    WhatsApp) nao e erro de digitacao, e escolha. Cobrar palavra por palavra nele
    enche o relatorio de ruido e enterra o achado que importa. Ja um texto que
    acentua o tempo todo e escorrega em algumas palavras esta com erro de
    verdade, e esse e o caso que precisa aparecer.

    O teste e de proporcao, nao de contagem: o texto tem que acentuar mais do que
    escorregar. Contagem absoluta nao serve, porque uma nota inteira sem acento
    com um nome proprio acentuado no meio passaria a ser cobrada palavra por
    palavra.
    """
    acentos = len(ACENTOS.findall(texto))
    faltando = len(re.findall(RE_ACENTO_FALTANDO, texto))
    if faltando == 0:
        return True
    return acentos > faltando


AQUI = os.path.dirname(os.path.abspath(__file__))
REGRAS_PADRAO = os.path.join(os.path.dirname(AQUI), "minhas-regras.json")


def carrega_regras(caminho):
    """Regras da pessoa: lista de {id, titulo, peso, regex, saida} num JSON."""
    if not caminho or not os.path.isfile(caminho):
        return []
    with open(caminho, encoding="utf-8") as fh:
        dados = json.load(fh)
    regras = []
    for r in dados.get("regras", dados if isinstance(dados, list) else []):
        if r.get("ativa", True) is False:
            continue
        re.compile(r["regex"])  # erro aqui aparece cedo, com o regex na mensagem
        regras.append((r["id"], r.get("titulo", r["id"]), int(r.get("peso", 2)),
                       r["regex"], r.get("saida", "")))
    return regras


def achados_de(texto, sem_pergunta_resposta=None):
    saida = []
    pula_acento = not cobra_acento(texto)
    sem_pr = sem_pergunta_resposta if sem_pergunta_resposta is not None else texto
    for pid, titulo, peso, regex, sugestao in TODOS:
        if pid == "acento-faltando" and pula_acento:
            continue
        alvo = sem_pr if pid == "pergunta-autorrespondida" else texto
        for m in re.finditer(regex, alvo):
            ini = max(0, m.start() - 60)
            fim = min(len(alvo), m.end() + 60)
            trecho = " ".join(alvo[ini:fim].split())
            saida.append({
                "id": pid, "padrao": titulo, "peso": peso,
                "trecho": trecho, "saida": sugestao,
            })
    saida.extend(afirmacoes_sem_fonte(texto))
    return saida


def arquivos_de(alvos, exts):
    for alvo in alvos:
        if os.path.isfile(alvo):
            yield alvo
            continue
        for raiz, dirs, nomes in os.walk(alvo):
            dirs[:] = [d for d in dirs if d not in
                       {".git", "node_modules", "dist", "build", ".worktrees"}]
            for n in sorted(nomes):
                if n.rsplit(".", 1)[-1].lower() in exts:
                    yield os.path.join(raiz, n)


def main():
    ap = argparse.ArgumentParser(description="Detector de texto com cara de IA")
    ap.add_argument("caminhos", nargs="*")
    ap.add_argument("--texto", help="revisa este texto direto, sem arquivo")
    ap.add_argument("--regras", default=REGRAS_PADRAO,
                    help="JSON com as suas regras (padrao: minhas-regras.json da skill)")
    ap.add_argument("--ext", default="md,html,htm,txt,page")
    ap.add_argument("--min", type=int, default=1, help="minimo de achados para listar")
    ap.add_argument("--peso", type=int, default=1, help="peso minimo do achado")
    ap.add_argument("--md", metavar="ARQUIVO", help="grava relatorio markdown")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    global TODOS
    TODOS = TODOS + carrega_regras(args.regras)
    if not args.caminhos and not args.texto:
        ap.error("passe um CAMINHO ou --texto")

    exts = {e.strip().lstrip(".").lower() for e in args.ext.split(",")}
    relatorio, total, por_padrao = [], 0, {}

    fontes = []
    if args.texto:
        fontes.append(("(texto)", (args.texto, args.texto)))
    for caminho in arquivos_de(args.caminhos, exts):
        try:
            fontes.append((caminho, extrai_texto(caminho)))
        except OSError:
            continue

    for caminho, textos in fontes:
        achados = [a for a in achados_de(*textos) if a["peso"] >= args.peso]
        if len(achados) < args.min:
            continue
        achados.sort(key=lambda a: -a["peso"])
        pontos = sum(a["peso"] for a in achados)
        relatorio.append({"arquivo": caminho, "pontos": pontos, "achados": achados})
        total += len(achados)
        for a in achados:
            por_padrao[a["padrao"]] = por_padrao.get(a["padrao"], 0) + 1

    relatorio.sort(key=lambda r: -r["pontos"])

    if args.json:
        print(json.dumps({"total": total, "arquivos": relatorio},
                         ensure_ascii=False, indent=1))
        return 0

    linhas = []
    linhas.append("# Revisao de texto: estruturas que soam geradas por IA")
    linhas.append("")
    linhas.append("%d achados em %d arquivos." % (total, len(relatorio)))
    linhas.append("")
    if por_padrao:
        linhas.append("| Padrao | Ocorrencias |")
        linhas.append("|---|---|")
        for p, q in sorted(por_padrao.items(), key=lambda x: -x[1]):
            linhas.append("| %s | %d |" % (p, q))
        linhas.append("")
    for r in relatorio:
        linhas.append("## %s" % r["arquivo"])
        linhas.append("")
        linhas.append("%d achados, %d pontos." % (len(r["achados"]), r["pontos"]))
        linhas.append("")
        for a in r["achados"]:
            linhas.append("- **%s** (peso %d)" % (a["padrao"], a["peso"]))
            linhas.append("  > ...%s..." % a["trecho"])
            linhas.append("  Saida: %s" % a["saida"])
        linhas.append("")
    texto = "\n".join(linhas)

    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(texto)
        print("relatorio em %s | %d achados em %d arquivos" %
              (args.md, total, len(relatorio)))
    else:
        print(texto)

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
