---
name: texto-sem-cara-de-ia
description: Tira a cara de IA de qualquer texto, e principalmente faz a mensagem soar como a própria pessoa falando com aquela pessoa ou aquele grupo. Lê o histórico da conversa (WhatsApp exportado, e-mails, DMs), monta o cartão de voz de quem escreve (como abre, "vc" ou "você", "pra" ou "para", tamanho, emoji, como fecha) e confere o rascunho contra ele. Olha também o agora da conversa: se a pessoa acabou de falar ali, não cumprimenta de novo; e propõe o texto em balões curtos, um envio por bloco, como se manda no celular. Depois procura as estruturas sintáticas que denunciam texto gerado (antítese negada, "não apenas X, mas Y", negação tripla, aforismo de fechamento, travessão). Use ao escrever, reescrever ou revisar mensagem, resposta, e-mail, post ou página, e sempre que alguém disser "tira a cara de IA", "isso parece robô", "deixa com o meu jeito", "escreve como eu escrevo pra ele", "revisa esse texto" ou "humaniza".
---

# Texto sem cara de IA

Duas perguntas, nesta ordem:

1. **Isso soa como eu falando com essa pessoa (ou com esse grupo)?** A mesma pessoa
   escreve de um jeito para o cliente, de outro para o sócio e de outro para o grupo
   da família. Um texto de IA soa estranho, antes de tudo, porque foge desse jeito:
   abre com "Olá!" quem sempre abre com "Fala", escreve "você" quem sempre escreve
   "vc", manda três parágrafos para quem recebe duas linhas.
2. **Tem estrutura de máquina?** O problema quase nunca é o vocabulário. São
   estruturas que se repetem: nega X para afirmar Y, três "sem" seguidos, a frase de
   efeito no fim. Uma vez é retórica; cinco vezes no mesmo texto é assinatura.

A pergunta que decide tudo: **uma pessoa escreveria essa frase falando com a outra?**
Se a resposta for "só num texto", reescreva.

## Quando o texto vai para uma pessoa ou um grupo

Esse é o caso principal. Siga na ordem e não pule o passo 1.

### 1. Ler o histórico antes de escrever

Pegue as mensagens que **a pessoa que escreve** já mandou **nessa conversa**. Não vale
o jeito dela em geral: vale o jeito com aquele destinatário.

- Se você tem um conector que lê o canal (WhatsApp, e-mail, Slack, Teams), leia a
  conversa inteira dos últimos 60 dias e salve num `.txt`, uma mensagem por linha no
  formato `[dd/mm/aaaa hh:mm] Nome: texto`.
- Se não tem, peça para a pessoa exportar a conversa do WhatsApp, sem mídia (o passo
  a passo está em [references/cartao-de-voz.md](references/cartao-de-voz.md)), ou colar
  pelo menos 10 mensagens que ela mandou para esse destinatário, separadas por linha
  em branco.
- Nunca escreva para alguém sem ter lido como a pessoa fala com ele. Sem histórico,
  diga isso e peça.

### 2. Montar o cartão de voz

```bash
python3 scripts/cartao_de_voz.py conversa.txt                  # mostra quem escreve
python3 scripts/cartao_de_voz.py conversa.txt --eu "Rafael"    # o cartão
```

O cartão mede, nas últimas 50 mensagens dela: como abre e como fecha, "vc" ou "você",
"pra" ou "para", "tá" ou "está", "a gente" ou "nós", quantas palavras por balão e
quantos balões por vez, emoji e quais, risada escrita, maiúscula no começo, ponto no
fim, exclamação, quebra de linha, lista ou negrito, travessão e as expressões que ela
repete. E mostra o outro lado: como a pessoa (ou o grupo) escreve de volta.

Leia o cartão inteiro e as mensagens também. O script conta; o tom (carinho, pressa,
ironia, o apelido que ela usa) você pega lendo.

O cartão traz também **o agora da conversa**: quando foi a última mensagem dela ali, o
que chegou depois e se ela costuma cumprimentar de novo quando volta a falar no mesmo
dia. Leia a conversa até a última linha, sempre, logo antes de escrever: o histórico de
ontem não mostra o que ela mandou há dez minutos.

### 3. Escrever dentro do cartão

1. **Conversa aberta não tem cumprimento.** Se ela falou ali há menos de 6 horas, nada de
   "Oi, pessoal. Tudo bem?" de novo: comece pelo assunto, ligando ao que foi dito
   ("Aproveitando o tópico, ...", "Sobre o que falei agora há pouco, ..."). Se alguém
   escreveu depois dela, responda isso antes ou junto.
2. O que a pessoa ditou ou pediu é o **briefing**, não a mensagem. Pegue o conteúdo e
   diga do jeito que ela diz para esse destinatário.
3. O jeito dela com essa pessoa vence qualquer regra de estilo, inclusive deste
   arquivo. Se ela usa emoji com essa pessoa, o texto pode ter emoji.
4. Chame o destinatário pelo nome ou apelido que ela já usa. Nunca invente apelido.
5. No WhatsApp, mensagem é poucas linhas curtas, como se digita no celular. Quem manda
   em blocos (vários balões seguidos, ou mensagens com quebra de linha) recebe o texto
   já dividido em balões, um envio por bloco: o script propõe a divisão no fim da
   conferência (`## Em balões`).
6. O jeito do outro lado conta também: quem escreve curto e carinhoso recebe curto e
   carinhoso, e as abreviações dele ("td", "vc", "!!") podem entrar se ela já escreve
   informal com ele.
7. Grupo é diferente de conversa a dois: veja como ela fala **naquele grupo**, que
   costuma ser mais curto e mais neutro do que no privado.
8. Um assunto por mensagem. Sem markdown, sem lista com marcador, sem negrito, a
   menos que ela escreva assim nessa conversa.
9. Link que a pessoa talvez não abra (estudo longo, site em inglês, conteúdo pago)
   fica de fora; ofereça: "se quiser, te mando o estudo".

### 4. Conferir o rascunho contra o cartão

```bash
python3 scripts/cartao_de_voz.py conversa.txt --eu "Rafael" --texto "o rascunho"
python3 scripts/cartao_de_voz.py conversa.txt --eu "Rafael" --rascunho rascunho.txt
```

Sai o agora da conversa e a lista do que foge do jeito dela (cumprimento repetido numa
conversa aberta, abertura diferente, "você" para quem escreve
"vc", longo demais, emoji onde ela nunca usa, parágrafos onde ela manda balões) e,
logo abaixo, as estruturas de IA do detector. Corrija e rode de novo até sobrar só
o que foi escolha consciente. No fim vem o rascunho dividido em balões.

Se a conferência é feita bem depois de exportar a conversa, passe `--agora "dd/mm/aaaa hh:mm"`
com a hora da última mensagem que você leu, ou exporte de novo.

### 5. Mostrar

Mostre, nesta ordem:

1. o cartão numa linha (a linha que começa com `>`), para a pessoa ver de onde veio o tom;
2. o texto final, com as quebras de linha reais e, para quem manda em blocos, já
   dividido em balões numerados (cada balão é um envio);
3. o que você mudou e por quê, em poucas linhas.

**Nada sai no nome de ninguém sem o sim da pessoa naquele texto exato.** Se ela muda
uma palavra, mostre de novo.

## Quando o texto é público (post, página, e-mail para quem não conhece, proposta)

Não há histórico com o leitor, então vale só a segunda pergunta. Se a pessoa tem textos
públicos dela (posts antigos, o site), monte o cartão com eles para pegar o tom.

```bash
python3 scripts/revisar_textos.py CAMINHO              # arquivo ou pasta (md, html, txt)
python3 scripts/revisar_textos.py --texto "o texto"    # direto
python3 scripts/revisar_textos.py . --peso 3           # só o que quase sempre soa automático
python3 scripts/revisar_textos.py . --md relatorio.md  # relatório em arquivo
```

O detector conta e pontua. **Ele não proíbe: quem decide é quem escreve.** Peso 3 quase
sempre soa automático e costuma sair. Peso 2 é suspeito quando repete. Peso 1 só
incomoda por densidade.

| Peso | Padrão | Marca |
|---|---|---|
| 3 | Antítese negada | Nega X para afirmar Y |
| 3 | Antítese invertida | "X, não Y" |
| 3 | Ausência retórica | "não é falta de X, é falta de Y" |
| 3 | Negação tripla | Três "sem" em sequência |
| 3 | "não apenas X, mas Y" | Escalada retórica |
| 3 | Aforismo de fechamento | Frase de efeito colada no fim |
| 3 | Palavra sem acento | Em texto que acentua no resto |
| 2 | Transformação ritual | "deixa de ser X e passa a ser Y" |
| 2 | Conector "É aqui que" | Emenda que aponta para a própria estrutura |
| 2 | Triplete nominal | "Um X, um Y, um Z" |
| 2 | Paralelismo com "cada" | "cada X..., e cada Y..." |
| 2 | Título de palavras-frase | "Fundação. Governança. IA." |
| 2 | Pergunta autorrespondida | Pergunta e resposta coladas |
| 2 | Travessão cercado de espaços | A marca de IA mais conhecida |
| 2 | Afirmação verificável sem fonte | Número, %, R$ ou lei sem link nem "segundo" |
| 1 | Muleta "vira" | "virar" como atalho de qualquer mudança |
| 1 | "em vez de" recorrente | Contraste por substituição virou fórmula |

O detalhe de cada um, com exemplo e reescrita, está em
[references/padroes.md](references/padroes.md).

**A armadilha mais comum** é a antítese negada, porque parece afiada. O teste: apague
a metade negativa e leia só o que sobrou. Se a frase continua de pé, a metade negativa
era enfeite.

**Fonte.** Todo número, percentual, valor, prazo ou lei que o leitor pode conferir tem
fonte nomeada, aberta e conferida na hora; existindo página oficial, o link vai na
própria frase. Fonte que não abre, ou que não diz o que o texto diz, derruba a frase.

## As regras da pessoa

O arquivo `minhas-regras.json`, na pasta da skill, guarda as regras de quem usa: frases
feitas que ela não aguenta mais, palavras que não usa, emoji proibido em texto de
trabalho. O detector lê esse arquivo sozinho. Quando a pessoa disser "nunca escreva X"
ou "eu não falo assim", ofereça adicionar uma regra lá, com um regex e a saída sugerida.

## O que esta skill não faz

- Não promete que o texto passa em detector de IA. Ela mede os sinais que uma pessoa
  percebe lendo; os detectores comerciais usam outros critérios.
- Não acha texto vazio. Frase bem construída e sem conteúdo passa limpa.
- Não decide sozinha. Lista de três itens quando o conteúdo tem três itens está certa;
  "em vez de" numa comparação técnica também.
- Não manda nada. Escreve, confere e mostra.
- Nada sai do computador: os scripts leem os arquivos e escrevem na tela.
