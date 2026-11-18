#!/usr/bin/env python3
"""
Cartao de voz: como VOCE escreve para uma pessoa ou um grupo, medido nas suas
proprias mensagens, e o quanto um rascunho foge disso.

A mesma pessoa escreve de um jeito para a mae, de outro para o cliente e de
outro para o grupo da pelada. Texto de IA soa estranho menos pelo vocabulario e
mais por fugir desse jeito: abre com "Ola!" quem sempre abre com "Fala", escreve
"voce" quem sempre escreve "vc", manda tres paragrafos para quem recebe duas
linhas. O cartao mede isso.

Uso:
    cartao_de_voz.py CONVERSA.txt                         lista quem escreve na conversa
    cartao_de_voz.py CONVERSA.txt --eu "Seu Nome"         monta o cartao
    cartao_de_voz.py CONVERSA.txt --eu "Seu Nome" --rascunho msg.txt
    cartao_de_voz.py CONVERSA.txt --eu "Seu Nome" --texto "a mensagem"
    cartao_de_voz.py CONVERSA.txt --eu "Seu Nome" --ultimas 60 --json
    cartao_de_voz.py CONVERSA.txt --eu "Seu Nome" --texto "..." --agora "18/11/2026 15:00"

Alem do jeito, o cartao olha o AGORA da conversa: quando foi a sua ultima mensagem e
o que chegou depois dela. Quem acabou de falar nao abre com "Oi, pessoal. Tudo bem?"
de novo. E propoe o rascunho em baloes, do jeito que se manda no celular.

CONVERSA.txt pode ser:
  - a conversa exportada do WhatsApp (iPhone ou Android, sem midia);
  - linhas no formato "[dd/mm/aaaa hh:mm] Nome: texto" (o que muitos leitores devolvem);
  - um arquivo so com mensagens suas, separadas por linha em branco (e-mails, DMs
    copiadas). Nesse caso nao precisa de --eu.

Nada sai do computador: o script le o arquivo e escreve na tela.
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from datetime import datetime

# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

INVISIVEIS = "‎‏‪‫‬‭‮﻿⁨⁩"

# [18/11/2026, 14:46:25] Nome: texto        (iPhone)
# [18/11/2026 14:46] Nome: texto            (leitores)
RE_COLCHETE = re.compile(
    r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)(?:\s*[APap]\.?\s?[Mm]\.?)?\]\s+"
    r"([^:]{1,60}?):\s?(.*)$")
# 18/11/2026 14:46 - Nome: texto            (Android)
RE_TRACO = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})(?:\s*[APap]\.?\s?[Mm]\.?)?\s+-\s+"
    r"([^:]{1,60}?):\s?(.*)$")
# linha de sistema do Android, sem autor: "18/11/2026 14:46 - Fulano entrou"
RE_SISTEMA = re.compile(r"^\[?\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}")

RE_MIDIA = re.compile(
    r"(?i)^\s*(?:<?\s*(?:m[íi]dia oculta|arquivo de m[íi]dia oculto|media omitted)\s*>?|"
    r"(?:imagem|[áa]udio|v[íi]deo|figurinha|documento|gif|sticker|image|audio|video|document)"
    r"\s+(?:ocultad[oa]|omitid[oa]|omitted)|"
    r"(?:essa|esta) mensagem foi apagada|mensagem apagada|this message was deleted|"
    r"you deleted this message|voc[êe] apagou esta mensagem|null|"
    r"\[(?:ciphertext|group|imagem|[áa]udio|audio|v[íi]deo|documento|figurinha|sticker)[^\]]*\]|"
    r"localiza[çc][ãa]o em tempo real.*|live location.*)\s*$")
RE_EDITADA = re.compile(r"\s*<(?:mensagem editada|this message was edited|editada)>\s*$", re.I)


def _data(d, h):
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%y %H:%M:%S", "%d/%m/%y %H:%M",
                "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime("%s %s" % (d, h), fmt)
        except ValueError:
            continue
    return None


def le_conversa(caminho):
    """Lista de mensagens {autor, quando, texto}. Sem formato de chat, devolve None."""
    with open(caminho, encoding="utf-8", errors="ignore") as fh:
        linhas = fh.read().splitlines()
    msgs, achou = [], 0
    for bruta in linhas:
        linha = bruta.strip(INVISIVEIS).rstrip()
        m = RE_COLCHETE.match(linha) or RE_TRACO.match(linha)
        if m:
            achou += 1
            d, h, autor, texto = m.groups()
            msgs.append({"autor": autor.strip(INVISIVEIS + " ~"), "quando": _data(d, h),
                         "texto": texto})
        elif RE_SISTEMA.match(linha):
            continue
        elif msgs:
            msgs[-1]["texto"] += "\n" + linha
    if achou < 2:
        return None
    limpas = []
    for m in msgs:
        t = RE_EDITADA.sub("", m["texto"].strip(INVISIVEIS)).strip()
        if not t or RE_MIDIA.match(t):
            continue
        m["texto"] = t
        limpas.append(m)
    return limpas


def le_blocos(texto, autor="eu"):
    """Texto solto: cada bloco separado por linha em branco e uma mensagem."""
    blocos = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    return [{"autor": autor, "quando": None, "texto": b} for b in blocos]


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def e_meu(autor, eu):
    return sem_acento(eu).lower() in sem_acento(autor).lower()


# --------------------------------------------------------------------------
# Medidas
# --------------------------------------------------------------------------

RE_EMOJI = re.compile(
    "[\U0001F1E6-\U0001F1FF\U0001F300-\U0001FAFF☀-➿⭐⭕❤‼⁉]")
RE_PALAVRA = re.compile(r"[A-Za-zÀ-ÿ0-9']+")
RE_RISADA = re.compile(r"(?i)\b(?:k{3,}|(?:ha){2,}h?|(?:he){2,}|(?:hu){2,}|rs(?:rs)*)\b")

# pares "jeito informal / jeito formal". O cartao diz qual dos dois voce usa.
PARES = [
    ("vc", r"\b(?:vc|vcs|vce)\b", "você", r"\bvoc[êe]s?\b"),
    ("pra", r"\b(?:pra|pras|pro|pros)\b", "para", r"\bpara\b"),
    ("tá", r"\bt[áa]\b|\bt[ôo]\b|\btamo\b|\bt[áa]va\b", "está", r"\best(?:á|a|ou|amos|ava)\b"),
    ("a gente", r"\ba gente\b", "nós", r"\bn[óo]s\b"),
    ("tu", r"\btu\b", "você", r"\bvoc[êe]\b"),
    ("blz/ok", r"\b(?:blz|beleza|ok|okay|show|fechou|top)\b", "certo/combinado",
     r"\b(?:certo|combinado|perfeito|de acordo)\b"),
    ("obg/vlw", r"\b(?:obg|obgd|vlw|valeu|brigad[oa])\b", "obrigado", r"\bobrigad[oa]s?\b"),
]

MARKDOWN = re.compile(r"(?m)^\s*(?:[-*•]\s|\d+[.)]\s|#{1,6}\s)|\*\*[^*]+\*\*")
TRAVESSAO = re.compile(r"[—–]")

PARADAS = set(("a o e de da do das dos em no na nos nas um uma uns umas que se por para pra "
               "com sem é eu você vc te me mas mais ou já não sim isso esse essa este esta "
               "aqui lá tá ta to tô vou vai ao aos as os foi ser tem ter como quando só "
               "the to and of in on is it").split())


def cabeca(texto):
    """Como a mensagem abre: a saudacao ate a primeira virgula ou exclamacao."""
    primeira = texto.strip().split("\n")[0]
    m = re.match(r"^([^,.!?\n]{1,28})[,.!?]", primeira)
    trecho = m.group(1) if m else " ".join(primeira.split()[:2])
    palavras = RE_PALAVRA.findall(trecho)
    if not palavras or len(palavras) > 4:
        return None
    return " ".join(palavras).lower()


def rabo(texto):
    """Como a mensagem fecha: a ultima linha curta."""
    ultima = texto.strip().split("\n")[-1].strip()
    palavras = RE_PALAVRA.findall(ultima)
    if not palavras or len(palavras) > 4:
        return None
    return " ".join(palavras).lower()


def falas(msgs, eu):
    """Agrupa baloes seus seguidos (menos de 5 min entre um e outro) numa fala so."""
    grupos, atual, ultimo = [], [], None
    for m in msgs:
        meu = e_meu(m["autor"], eu)
        perto = (ultimo is not None and m["quando"] and ultimo["quando"]
                 and (m["quando"] - ultimo["quando"]).total_seconds() < 300)
        if meu and atual and perto:
            atual.append(m)
        elif meu:
            if atual:
                grupos.append(atual)
            atual = [m]
        else:
            if atual:
                grupos.append(atual)
            atual = []
        ultimo = m
    if atual:
        grupos.append(atual)
    return grupos


def pct(n, d):
    return round(100.0 * n / d) if d else 0


def medir(baloes, turnos=None):
    """Medidas de uma lista de textos (baloes). turnos: lista de listas de textos."""
    turnos = turnos or [[b] for b in baloes]
    n = len(baloes)
    tamanhos = [len(RE_PALAVRA.findall(b)) for b in baloes]
    juntos = "\n".join(baloes)
    baixo = juntos.lower()

    pares = {}
    for nome_a, re_a, nome_b, re_b in PARES:
        qa, qb = len(re.findall(re_a, baixo)), len(re.findall(re_b, baixo))
        if qa or qb:
            pares[nome_a + " x " + nome_b] = {"informal": nome_a, "formal": nome_b,
                                              "qa": qa, "qb": qb}

    emojis = RE_EMOJI.findall(juntos)
    aberturas = Counter(c for c in (cabeca(t[0]) for t in turnos) if c)
    fechos = Counter(c for c in (rabo(t[-1]) for t in turnos) if c)

    palavras = [sem_acento(p.lower()) for p in RE_PALAVRA.findall(juntos)]
    bigramas = Counter()
    for b in baloes:
        ps = [sem_acento(p.lower()) for p in RE_PALAVRA.findall(b)]
        for i in range(len(ps) - 1):
            if ps[i] in PARADAS and ps[i + 1] in PARADAS:
                continue
            bigramas[ps[i] + " " + ps[i + 1]] += 1

    return {
        "baloes": n,
        "falas": len(turnos),
        "palavras_mediana": int(statistics.median(tamanhos)) if tamanhos else 0,
        "palavras_p90": sorted(tamanhos)[int(0.9 * (n - 1))] if tamanhos else 0,
        "baloes_por_fala": round(statistics.mean(len(t) for t in turnos), 1) if turnos else 0,
        "quebra_de_linha_pct": pct(sum(1 for b in baloes if "\n" in b), n),
        "comeca_maiuscula_pct": pct(sum(1 for b in baloes if b[:1].isupper()), n),
        "termina_ponto_pct": pct(sum(1 for b in baloes if b.rstrip().endswith(".")), n),
        "exclamacao_pct": pct(sum(1 for b in baloes if "!" in b), n),
        "reticencias_pct": pct(sum(1 for b in baloes if "..." in b or "…" in b), n),
        "risada_pct": pct(sum(1 for b in baloes if RE_RISADA.search(b)), n),
        "emoji_pct": pct(sum(1 for b in baloes if RE_EMOJI.search(b)), n),
        "emojis": [e for e, _ in Counter(emojis).most_common(5)],
        "markdown_pct": pct(sum(1 for b in baloes if MARKDOWN.search(b)), n),
        "travessao_pct": pct(sum(1 for b in baloes if TRAVESSAO.search(b)), n),
        "pares": pares,
        "aberturas": aberturas.most_common(5),
        "fechos": [f for f in fechos.most_common(5) if f[1] >= 2],
        "expressoes": [b for b, q in bigramas.most_common(8) if q >= 3],
        "_palavras": len(palavras),
    }


# --------------------------------------------------------------------------
# O agora da conversa
# --------------------------------------------------------------------------

RE_CUMPRIMENTO = re.compile(
    r"^\W*(?:oi+|ola|opa|fala|e ai|eai|bom dia|boa tarde|boa noite|tudo bem|tudo bom|tudo certo|"
    r"como vai|salve|hey|hello|hi)\b")
RECENTE_MIN = 6 * 60  # menos de 6 horas desde a sua ultima: a conversa ainda esta aberta


def cumprimenta(texto):
    primeira = sem_acento(texto.strip().split("\n")[0].lower())
    return bool(RE_CUMPRIMENTO.match(primeira))


def tempo(minutos):
    if minutos < 1:
        return "agora mesmo"
    if minutos < 60:
        return "%d min" % minutos
    if minutos < 48 * 60:
        return "%d h" % round(minutos / 60)
    return "%d dias" % round(minutos / 1440)


def momento(msgs, eu, turnos, agora):
    """Quando voce falou por ultimo, o que veio depois e se voce costuma cumprimentar de novo."""
    minhas = [m for m in msgs if e_meu(m["autor"], eu) and m["quando"]]
    if not minhas:
        return None
    ultima = minhas[-1]
    minutos = max(0, (agora - ultima["quando"]).total_seconds() / 60)
    depois = [m for m in msgs if m["quando"] and m["quando"] > ultima["quando"]
              and not e_meu(m["autor"], eu)]
    # nas suas falas que vieram menos de 6h depois de outra sua, voce cumprimentou?
    com_data = [t for t in turnos if t[0]["quando"]]
    retomadas = cumprimentos = 0
    for anterior, atual in zip(com_data, com_data[1:]):
        gap = (atual[0]["quando"] - anterior[-1]["quando"]).total_seconds() / 60
        if gap < RECENTE_MIN:
            retomadas += 1
            cumprimentos += cumprimenta(atual[0]["texto"])
    return {
        "minutos": round(minutos),
        "quando": ultima["quando"].strftime("%d/%m %H:%M"),
        "sua_ultima": " ".join(ultima["texto"].split())[:140],
        "depois_de_voce": [{"autor": m["autor"], "texto": " ".join(m["texto"].split())[:120]}
                           for m in depois[-5:]],
        "retomadas": retomadas,
        "recumprimenta_pct": pct(cumprimentos, retomadas) if retomadas else None,
    }


RE_FRASES = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Úa-zà-ú0-9@h])")


def propor_baloes(texto, c):
    """Quebra o rascunho em baloes: uma linha por balao, e linha longa por frase."""
    limite = max(2 * c["palavras_mediana"], 15)
    baloes = []
    for linha in [l.strip() for l in texto.strip().splitlines() if l.strip()]:
        if len(RE_PALAVRA.findall(linha)) <= limite:
            baloes.append(linha)
            continue
        baloes.extend(f.strip() for f in RE_FRASES.split(linha) if f.strip())
    return baloes


def manda_em_baloes(c):
    return c["baloes_por_fala"] >= 1.5 or c["quebra_de_linha_pct"] >= 25


# --------------------------------------------------------------------------
# Comparacao
# --------------------------------------------------------------------------

def preferido(par):
    """Qual lado do par a pessoa usa, ou None se nao da para dizer."""
    qa, qb = par["qa"], par["qb"]
    if qa + qb < 3:
        return None
    if qa >= 2 * qb:
        return "informal"
    if qb >= 2 * qa:
        return "formal"
    return None


def diferencas(c, agora, rascunho):
    """O que no rascunho foge do cartao. Cada item: (peso, frase)."""
    saida = []
    texto = rascunho.strip()
    baixo = texto.lower()

    # cumprimento repetido: voce acabou de falar aqui
    if agora and agora["minutos"] < RECENTE_MIN and cumprimenta(texto):
        costume = agora["recumprimenta_pct"]
        if costume is None or costume < 50:
            saida.append((3, "Cumprimenta de novo, e você falou aqui há %s (\"%s\"). Continue a "
                             "conversa: comece pelo assunto (\"Aproveitando...\", \"Sobre...\")%s."
                          % (tempo(agora["minutos"]), agora["sua_ultima"][:70],
                             "" if costume is None else
                             "; quando volta a falar no mesmo dia, você cumprimenta em %d%% das vezes" % costume)))

    # baloes
    linhas = [l for l in texto.splitlines() if l.strip()]
    if manda_em_baloes(c) and len(propor_baloes(texto, c)) > 1 and len(linhas) < len(propor_baloes(texto, c)):
        saida.append((2, "Você costuma mandar em blocos curtos (%.1f balões por vez, quebra de linha em %d%%). "
                         "Mande em balões separados, como no fim deste relatório."
                      % (c["baloes_por_fala"], c["quebra_de_linha_pct"])))

    # tamanho
    total = sum(len(RE_PALAVRA.findall(b)) for b in re.split(r"\n\s*\n", texto))
    teto = max(c["palavras_p90"], c["palavras_mediana"]) * max(1, round(c["baloes_por_fala"]))
    if teto and total > 1.5 * teto:
        saida.append((3, "Longo demais: %d palavras. Você costuma mandar %d por balão (até %d), "
                         "e %.1f balões por vez." % (total, c["palavras_mediana"],
                                                     c["palavras_p90"], c["baloes_por_fala"])))

    # pares
    for nome, par in c["pares"].items():
        lado = preferido(par)
        if not lado:
            continue
        cfg = next(p for p in PARES if p[0] == par["informal"] and p[2] == par["formal"])
        usa_a = re.search(cfg[1], baixo)
        usa_b = re.search(cfg[3], baixo)
        if lado == "informal" and usa_b and not usa_a:
            saida.append((2, "Você escreve \"%s\" (%dx) e quase nunca \"%s\" (%dx). O rascunho usa \"%s\"."
                          % (par["informal"], par["qa"], par["formal"], par["qb"], usa_b.group(0))))
        if lado == "formal" and usa_a and not usa_b:
            saida.append((2, "Você escreve \"%s\" (%dx) e quase nunca \"%s\" (%dx). O rascunho usa \"%s\"."
                          % (par["formal"], par["qb"], par["informal"], par["qa"], usa_a.group(0))))

    # abertura
    abre = cabeca(texto)
    suas = [a for a, _ in c["aberturas"]]
    aberta = agora and agora["minutos"] < RECENTE_MIN
    if abre and suas and c["falas"] >= 5 and abre not in suas and not (aberta and not cumprimenta(texto)):
        saida.append((2, "Abre com \"%s\". Você costuma abrir com: %s."
                      % (abre, ", ".join('"%s"' % a for a in suas[:3]))))

    # emoji
    tem_emoji = bool(RE_EMOJI.search(texto))
    if tem_emoji and c["emoji_pct"] == 0 and c["baloes"] >= 10:
        saida.append((3, "Tem emoji, e você não usou nenhum nas últimas %d mensagens." % c["baloes"]))
    if not tem_emoji and c["emoji_pct"] >= 50:
        saida.append((1, "Sem emoji, e você usa em %d%% das mensagens (%s)."
                      % (c["emoji_pct"], " ".join(c["emojis"][:3]))))

    # markdown e travessao
    if MARKDOWN.search(texto) and c["markdown_pct"] < 10:
        saida.append((3, "Tem lista, título ou negrito, e você quase nunca formata mensagem (%d%%)."
                      % c["markdown_pct"]))
    if TRAVESSAO.search(texto) and c["travessao_pct"] < 5:
        saida.append((3, "Tem travessão (—), e você não usa (%d%%). É a marca de IA mais conhecida."
                      % c["travessao_pct"]))

    # pontuacao e caixa
    if texto.endswith(".") and c["termina_ponto_pct"] <= 20 and c["baloes"] >= 10:
        saida.append((1, "Termina com ponto final. Você fecha com ponto em só %d%% das mensagens."
                      % c["termina_ponto_pct"]))
    if texto[:1].isupper() and c["comeca_maiuscula_pct"] <= 20 and c["baloes"] >= 10:
        saida.append((1, "Começa com maiúscula. Você começa com minúscula em %d%% das mensagens."
                      % (100 - c["comeca_maiuscula_pct"])))
    if "!" in texto and c["exclamacao_pct"] <= 5 and c["baloes"] >= 10:
        saida.append((1, "Tem exclamação, e você quase não usa (%d%%)." % c["exclamacao_pct"]))
    if "!" not in texto and c["exclamacao_pct"] >= 60:
        saida.append((1, "Sem exclamação, e você usa em %d%% das mensagens." % c["exclamacao_pct"]))
    if "\n\n" in texto and c["quebra_de_linha_pct"] <= 10 and c["baloes"] >= 10:
        saida.append((2, "Tem parágrafos. Você manda balões curtos, sem quebra de linha. "
                         "Se for o caso, divida em balões."))

    saida.sort(key=lambda x: -x[0])
    return saida


# --------------------------------------------------------------------------
# Saida
# --------------------------------------------------------------------------

def linha_unica(c):
    """O cartao numa linha, para mostrar em cima do rascunho."""
    partes = []
    if c["aberturas"]:
        partes.append("abre com \"%s\"" % c["aberturas"][0][0])
    for par in c["pares"].values():
        lado = preferido(par)
        if lado:
            partes.append(par[lado])
    partes.append("~%d palavras por balão" % c["palavras_mediana"])
    if c["baloes_por_fala"] >= 1.5:
        partes.append("%.0f balões por vez" % c["baloes_por_fala"])
    partes.append("emoji %s" % ("sim " + "".join(c["emojis"][:3]) if c["emoji_pct"] >= 20 else
                                "raro" if c["emoji_pct"] else "nunca"))
    if c["risada_pct"] >= 10:
        partes.append("ri escrito")
    if c["fechos"]:
        partes.append("fecha com \"%s\"" % c["fechos"][0][0])
    return "; ".join(partes)


def imprime_agora(agora):
    p = print
    p()
    p("## Agora nesta conversa")
    p()
    if not agora:
        p("Sem data nas mensagens: não dá para saber quando você falou por último. Pergunte.")
        return
    p("Sua última mensagem aqui: %s, há %s: \"%s\"" % (agora["quando"], tempo(agora["minutos"]),
                                                        agora["sua_ultima"]))
    if agora["depois_de_voce"]:
        p()
        p("Depois dela, escreveram:")
        for m in agora["depois_de_voce"]:
            p("- %s: %s" % (m["autor"], m["texto"]))
    else:
        p("Ninguém escreveu depois dela.")
    p()
    if agora["minutos"] < RECENTE_MIN:
        p("A conversa está aberta: não cumprimente de novo; continue de onde parou.")
    if agora["recumprimenta_pct"] is not None:
        p("Quando volta a falar em menos de 6 h, você cumprimenta em %d%% das vezes (%d casos)."
          % (agora["recumprimenta_pct"], agora["retomadas"]))


def imprime_cartao(nome, c, grupo, outros):
    p = print
    p("# Cartão de voz: %s nesta conversa" % nome)
    p()
    p("Base: suas últimas %d mensagens (%d falas). Em uma linha:" % (c["baloes"], c["falas"]))
    p()
    p("> " + linha_unica(c))
    p()
    p("| O quê | Você |")
    p("|---|---|")
    p("| Tamanho | %d palavras por balão (mediana), até %d |" % (c["palavras_mediana"], c["palavras_p90"]))
    p("| Balões por vez | %.1f |" % c["baloes_por_fala"])
    if c["aberturas"]:
        p("| Como abre | %s |" % ", ".join('"%s" (%d)' % a for a in c["aberturas"]))
    if c["fechos"]:
        p("| Como fecha | %s |" % ", ".join('"%s" (%d)' % f for f in c["fechos"]))
    for par in c["pares"].values():
        lado = preferido(par)
        marca = " (usa %s)" % par[lado] if lado else " (mistura)"
        p("| %s x %s | %d x %d%s |" % (par["informal"], par["formal"], par["qa"], par["qb"], marca))
    p("| Emoji | %d%% das mensagens %s |" % (c["emoji_pct"], " ".join(c["emojis"])))
    p("| Risada escrita | %d%% |" % c["risada_pct"])
    p("| Começa com maiúscula | %d%% |" % c["comeca_maiuscula_pct"])
    p("| Termina com ponto | %d%% |" % c["termina_ponto_pct"])
    p("| Exclamação | %d%% |" % c["exclamacao_pct"])
    p("| Quebra de linha no balão | %d%% |" % c["quebra_de_linha_pct"])
    p("| Lista ou negrito | %d%% |" % c["markdown_pct"])
    p("| Travessão | %d%% |" % c["travessao_pct"])
    if c["expressoes"]:
        p("| Expressões que repete | %s |" % ", ".join('"%s"' % e for e in c["expressoes"]))
    if outros:
        p()
        p("O outro lado (%s): %d palavras por balão, emoji em %d%%, risada em %d%%."
          % ("o grupo, %d pessoas" % grupo if grupo > 1 else "a pessoa",
             outros["palavras_mediana"], outros["emoji_pct"], outros["risada_pct"]))
    if c["baloes"] < 10:
        p()
        p("Atenção: menos de 10 mensagens suas. O cartão é um palpite; peça mais histórico.")


def main():
    ap = argparse.ArgumentParser(description="Cartão de voz: como você escreve nesta conversa")
    ap.add_argument("conversa", help="conversa exportada (.txt) ou mensagens suas separadas por linha em branco")
    ap.add_argument("--eu", help="seu nome como aparece na conversa (basta um pedaço)")
    ap.add_argument("--ultimas", type=int, default=50, help="quantas mensagens suas usar (padrão 50)")
    ap.add_argument("--rascunho", help="arquivo com o rascunho a conferir")
    ap.add_argument("--texto", help="o rascunho direto, sem arquivo")
    ap.add_argument("--agora", help="data e hora de referência, dd/mm/aaaa hh:mm (padrão: agora)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    agora_dt = datetime.now()
    if a.agora:
        d, _, h = a.agora.partition(" ")
        agora_dt = _data(d, h or "00:00") or agora_dt

    msgs = le_conversa(a.conversa)
    if msgs is None:
        with open(a.conversa, encoding="utf-8", errors="ignore") as fh:
            msgs = le_blocos(fh.read())
        a.eu = a.eu or "eu"

    if not a.eu:
        autores = Counter(m["autor"] for m in msgs)
        print("Quem escreve nesta conversa (passe o seu com --eu):")
        for autor, q in autores.most_common():
            print("  %5d  %s" % (q, autor))
        return 2

    minhas = [m for m in msgs if e_meu(m["autor"], a.eu)]
    if not minhas:
        print("Nenhuma mensagem de \"%s\". Rode sem --eu para ver os nomes." % a.eu)
        return 2

    turnos = falas(msgs, a.eu)
    # corta nas ultimas N mensagens suas, mantendo as falas inteiras
    escolhidos, conta = [], 0
    for t in reversed(turnos):
        escolhidos.insert(0, t)
        conta += len(t)
        if conta >= a.ultimas:
            break
    baloes = [m["texto"] for t in escolhidos for m in t]
    cartao = medir(baloes, [[m["texto"] for m in t] for t in escolhidos])

    deles = [m for m in msgs if not e_meu(m["autor"], a.eu)][-a.ultimas * 2:]
    outros = medir([m["texto"] for m in deles]) if deles else None
    grupo = len(set(m["autor"] for m in deles))

    rascunho = a.texto
    if a.rascunho:
        with open(a.rascunho, encoding="utf-8") as fh:
            rascunho = fh.read()
    agora = momento(msgs, a.eu, turnos, agora_dt)
    difs = diferencas(cartao, agora, rascunho) if rascunho else None
    baloes_propostos = propor_baloes(rascunho, cartao) if rascunho else None
    estrutura = []
    if rascunho:
        try:
            sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
            import revisar_textos as rt
            rt.TODOS = rt.TODOS + rt.carrega_regras(rt.REGRAS_PADRAO)
            estrutura = rt.achados_de(rascunho)
        except Exception as erro:  # o cartao vale sozinho; o detector e um extra
            print("(detector de estrutura indisponível: %s)" % erro, file=sys.stderr)

    if a.json:
        cartao.pop("_palavras", None)
        print(json.dumps({"cartao": cartao, "linha": linha_unica(cartao),
                          "outro_lado": outros and {k: outros[k] for k in
                                                    ("palavras_mediana", "emoji_pct", "risada_pct")},
                          "pessoas_do_outro_lado": grupo,
                          "agora": agora,
                          "baloes_propostos": baloes_propostos,
                          "diferencas": difs and [{"peso": p, "o_que": t} for p, t in difs],
                          "estrutura_de_ia": estrutura},
                         ensure_ascii=False, indent=1))
        return 1 if (difs or estrutura) else 0

    imprime_cartao(a.eu, cartao, grupo, outros)
    imprime_agora(agora)
    if rascunho is not None:
        print()
        print("## O rascunho contra o cartão")
        print()
        if not difs:
            print("Nada foge do seu jeito nesta conversa.")
        for peso, frase in difs or []:
            print("- (peso %d) %s" % (peso, frase))
        if estrutura:
            print()
            print("## Estrutura que soa como IA")
            print()
            for e in sorted(estrutura, key=lambda x: -x["peso"]):
                print("- (peso %d) %s: \"...%s...\" %s" % (e["peso"], e["padrao"], e["trecho"], e["saida"]))
        if len(baloes_propostos) > 1:
            print()
            print("## Em balões (um envio por bloco)")
            for i, b in enumerate(baloes_propostos, 1):
                print()
                print("[%d] %s" % (i, b))
    return 1 if (difs or estrutura) else 0


if __name__ == "__main__":
    sys.exit(main())
