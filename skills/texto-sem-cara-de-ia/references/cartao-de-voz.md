# Cartão de voz

O cartão de voz é o retrato de como uma pessoa escreve **numa conversa específica**,
medido nas mensagens dela. Serve para escrever no jeito dela e para conferir se um
rascunho foge desse jeito.

## De onde vem o histórico

### Exportar uma conversa do WhatsApp

No iPhone:

1. Abra a conversa (ou o grupo) e toque no nome no topo.
2. Role até o fim e toque em **Exportar conversa**.
3. Escolha **Sem mídia** e salve o arquivo (ele vem em `.zip`; dentro há um `.txt`).

No Android:

1. Abra a conversa (ou o grupo), toque nos três pontinhos, **Mais**, **Exportar conversa**.
2. Escolha **Sem mídia** e salve o `.txt`.

Mande o `.txt` (ou o `.zip`, que o Claude abre) na conversa com o Claude.

A conversa exportada traz as mensagens de todo mundo. O cartão usa só as suas para o
seu jeito, e as dos outros para mostrar como o outro lado escreve.

### Sem exportação

Cole num arquivo pelo menos 10 mensagens que você mandou para aquela pessoa, separadas
por uma linha em branco. Serve para e-mail, LinkedIn, Instagram, Slack. Nesse caso não
precisa de `--eu`.

### Com um conector

Se o Claude tem acesso ao canal (um leitor de WhatsApp, o e-mail, o Slack), ele lê a
conversa e grava no formato `[dd/mm/aaaa hh:mm] Nome: texto`, uma mensagem por linha.
Mensagem de várias linhas continua nas linhas de baixo.

## O que o cartão mede

| Medida | Por que importa |
|---|---|
| Como abre ("fala", "oi", "bom dia") | É a primeira coisa que a pessoa lê, e a que mais denuncia |
| Como fecha ("abraço", "valeu") | A segunda |
| "vc" ou "você", "pra" ou "para", "tá" ou "está", "a gente" ou "nós", "tu" | Registro: o quanto a conversa é informal |
| "blz/ok/show" ou "certo/combinado", "valeu/obg" ou "obrigado" | Idem |
| Palavras por balão e balões por vez | Quem manda três balões de cinco palavras não manda um parágrafo de sessenta |
| Emoji, quais | Quem nunca usa, não começa agora; quem sempre usa, estranha a falta |
| Risada escrita (kkk, rs, haha) | Tom |
| Maiúscula no começo, ponto no fim, exclamação | Quem escreve tudo minúsculo e sem ponto denuncia um texto "certinho" |
| Quebra de linha, lista, negrito | Mensagem com marcador e negrito é a cara do texto gerado |
| Travessão | Quase ninguém digita |
| Expressões que repete | O vocabulário próprio da pessoa com aquele destinatário |
| O outro lado | Como a pessoa ou o grupo escreve de volta: o tom da conversa |
| O agora | Sua última mensagem ali, há quanto tempo, o que chegou depois, e se você cumprimenta de novo quando volta a falar no mesmo dia |
| Balões | O rascunho dividido em blocos curtos, um envio por bloco, quando você manda assim |

As últimas 50 mensagens são o padrão (`--ultimas` muda). Menos de 10 mensagens dão um
palpite, e o cartão avisa.

## O agora da conversa

Quem acabou de falar num grupo e volta com "Oi, pessoal. Tudo bem?" denuncia que o
texto foi escrito fora da conversa. O cartão mostra a sua última mensagem e o que
chegou depois. Com menos de 6 horas, a conversa está aberta: o rascunho que começa
cumprimentando leva peso 3, a menos que o seu histórico mostre que você cumprimenta
de novo mesmo assim. Comece pelo assunto: "Aproveitando o tópico, ...".

A hora de referência é a do computador. Conferindo uma conversa exportada há dias, use
`--agora "dd/mm/aaaa hh:mm"`.

## Balões

Muita gente manda em blocos: três ou quatro mensagens curtas seguidas, em vez de um
parágrafo. Quando o histórico mostra isso, a conferência termina com o rascunho
dividido (`## Em balões`): uma linha por balão, e linha longa quebrada por frase.
Cada balão é um envio.

## Como ler a conferência

Cada diferença vem com peso:

- **peso 3**: quase certo que soa estranho (cumprimento numa conversa aberta, emoji onde nunca houve, travessão,
  lista em mensagem, texto muito mais longo que o normal);
- **peso 2**: foge do jeito de sempre ("você" para quem escreve "vc", abertura nova,
  parágrafos para quem manda balões);
- **peso 1**: detalhe (ponto final, maiúscula, exclamação).

Nem toda diferença é erro. Uma mensagem séria para alguém com quem a conversa costuma
ser leve pode, e deve, ser diferente. A conferência mostra; a pessoa decide.

## Limites

- O script conta. Carinho, ironia, pressa e apelido você pega lendo as mensagens.
- Conversa que mudou de tom (de formal para próxima, por exemplo) pede um `--ultimas`
  menor, para pegar o tom de agora.
- Um grupo grande e barulhento diz pouco sobre você se você quase não fala nele. Nesse
  caso, olhe o outro lado e as poucas mensagens suas com atenção.
