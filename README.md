# Texto sem cara de IA

Uma skill para o Claude tirar a cara de IA dos seus textos e, principalmente, fazer a mensagem
soar como você falando com aquela pessoa ou aquele grupo.

Ela lê o histórico da conversa, entende como você costuma escrever ali (como abre, se escreve
"vc" ou "você", "pra" ou "para", o tamanho das mensagens, se usa emoji, como fecha) e confere o
rascunho contra esse jeito. Depois procura as estruturas que denunciam texto gerado, como
"não é X, é Y", "não apenas X, mas Y", três "sem" seguidos e o travessão.

## Um exemplo

O Rafael sempre escreve para a Marina assim: "fala Marina", tudo minúsculo, duas ou três
mensagens curtas, "pra", "show, valeu". O Claude escreveu:

```
Olá, Marina! Espero que você esteja bem. Gostaria de informar que o pagamento não é apenas uma formalidade, mas um compromisso — e já está programado.
```

A skill aponta:

```
- (peso 3) Tem travessão (—), e você não usa (0%). É a marca de IA mais conhecida.
- (peso 2) Abre com "olá". Você costuma abrir com: "fala marina", "show", "pode deixar".
- (peso 1) Começa com maiúscula. Você começa com minúscula em 100% das mensagens.
- (peso 1) Tem exclamação, e você quase não usa (0%).
- (peso 3) "não apenas X, mas Y": fique com o item mais forte.
```

E o texto vira:

```
fala Marina
pagamento programado pra quinta
```

## Como instalar

Você precisa do Claude no computador (claude.ai/download), com o Claude Code.

Peça ao Claude:

```
Instale para mim a skill texto-sem-cara-de-ia com o comando
npx skills add guimreis/texto-sem-cara-de-ia -g -y
```

Se ele disser que falta o Node.js, deixe ele te guiar na instalação. Depois, abra uma conversa nova.

### No Claude.ai (site e aplicativo)

1. Baixe o [texto-sem-cara-de-ia.zip](https://github.com/guimreis/texto-sem-cara-de-ia/raw/main/docs/texto-sem-cara-de-ia.zip).
2. No Claude.ai, abra Configurações, procure a área de Skills (em Capacidades) e envie o zip.
3. Numa conversa nova, mande a conversa exportada e peça a mensagem.

Os nomes dos menus podem mudar. Se não achar, procure por "Skills" na ajuda do Claude.

## Como usar

1. Exporte a conversa do WhatsApp com a pessoa ou o grupo, **sem mídia** (iPhone: toque no nome
   da conversa, Exportar conversa; Android: três pontinhos, Mais, Exportar conversa). Para
   e-mail ou outra rede, cole umas 10 mensagens suas para aquela pessoa num arquivo.
2. Numa conversa nova com o Claude, mande o arquivo e diga:

```
Escreve uma mensagem pro Rafael dizendo que a nota sai sexta, do jeito que eu falo com ele.
```

ou

```
Revisa esse texto e tira a cara de IA.
```

O Claude mostra o seu cartão de voz numa linha, o texto e o que mudou. Nada é enviado: ele
escreve, confere e te mostra.

## Faça a sua versão

A skill é uma base. Copie, mude e coloque o seu jeito:

- `skills/texto-sem-cara-de-ia/minhas-regras.json` guarda as suas regras: frases feitas que você
  não aguenta mais, palavras que não usa, emoji proibido no trabalho. Peça ao Claude:
  "adiciona uma regra no meu minhas-regras.json para nunca usar 'vale ressaltar'".
- `skills/texto-sem-cara-de-ia/references/padroes.md` é o catálogo dos padrões de IA, com
  exemplo e reescrita.
- `skills/texto-sem-cara-de-ia/scripts/` tem os dois scripts em Python, sem dependência:
  `cartao_de_voz.py` (o seu jeito numa conversa) e `revisar_textos.py` (as estruturas de IA).

Tudo roda no seu computador. Nenhuma conversa sai da sua máquina.

## Quem fez

Feito por Guilherme Reis. Ensino empresários e profissionais a trabalhar com IA no dia a dia.

- Instagram: [@guilhermereis.ai](https://www.instagram.com/guilhermereis.ai/)
- Comunidade no WhatsApp, com aula ao vivo toda segunda: [entrar no grupo](https://chat.whatsapp.com/LncD1JNhpog7246d8waj74)

Licença MIT: use, mude e compartilhe à vontade.
