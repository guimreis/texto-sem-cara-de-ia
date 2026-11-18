# Padrões de texto que soam gerados por IA

Catálogo de referência da skill `texto-sem-cara-de-ia`. Nasceu como guia de revisão
de um site e vale para qualquer texto. O problema não está no vocabulário: está em
**estruturas sintáticas** que se repetem. Um padrão usado uma vez é retórica. O
mesmo padrão cinco vezes na mesma página é assinatura de máquina.

Todos os exemplos ruins abaixo saíram de textos reais, publicados.

Detector: `python3 scripts/revisar_textos.py`

```bash
python3 scripts/revisar_textos.py .                       # tudo
python3 scripts/revisar_textos.py . --ext md,html         # por extensão
python3 scripts/revisar_textos.py site/sobre.html        # um arquivo
python3 scripts/revisar_textos.py . --md relatorio.md     # gera arquivo
python3 scripts/revisar_textos.py . --min 3               # só com 3+ achados
python3 scripts/revisar_textos.py . --peso 3              # só peso 3
```

O detector conta e pontua. Ele não proíbe: quem decide é quem escreve.

---

## Como usar este guia

Cada padrão tem peso. Peso 3 quase sempre soa automático e deve sair. Peso 2 é
suspeito quando repete. Peso 1 só incomoda por densidade, e uma ocorrência
isolada normalmente pode ficar.

A pergunta de revisão é sempre a mesma: **uma pessoa escreveria essa frase
falando com outra pessoa?** Se a resposta for "só num texto", reescreva.

---

## Peso 3

### 1. Antítese negada

Nega X para afirmar Y. É a estrutura mais reconhecível de texto gerado.

> Não começamos pela ferramenta. Começamos pela decisão que precisa ficar de pé.

> O que falta não é ferramenta, é o caminho auditável entre o dado e a decisão.

> Não é workshop, é evidência consultável.

**Saída:** afirme Y direto. O leitor não precisa do X que você descartou.

> Falta o caminho auditável entre o dado e a decisão.

### 2. Ausência retórica

Variante da anterior, na forma "não é falta de X, é falta de Y". Soa profundo e
não acrescenta informação.

> O problema não é ausência de dado, é ausência de caminho confiável.

**Saída:** diga o que falta, uma vez.

### 3. Negação tripla

Três "sem" em sequência. Ritmo de slogan.

> Sem contrato contínuo, sem pacote de horas, sem fila compartilhada.

**Saída:** escolha a negação que importa e corte as outras duas. Ou diga no
positivo: "Cada demanda é paga em separado."

### 4. Aforismo de fechamento

Sentença de efeito colada no fim do parágrafo, geralmente com uma metáfora de
prazo ou de dívida.

> Modelo sem ciclo de vida é dívida técnica com data marcada.

**Saída:** termine no fato. O aforismo enfraquece o que veio antes.

> Sem ciclo de vida, o modelo para de acompanhar a operação e ninguém percebe.

### 5. "não apenas X, mas Y"

Escalada retórica clássica.

> O custo de uma decisão ruim não é apenas financeiro, é reputacional, é de
> carreira, é irreversível.

**Saída:** fique com o item mais forte.

---

## Peso 2

### 6. Transformação ritual

"deixa de ser X e passa a ser Y" é transição pré-fabricada.

> Governança deixa de ser política e passa a ser suposição.

**Saída:** descreva o estado final.

> A governança escrita na política não se sustenta no ambiente real.

### 7. Conector "É aqui que" / "É por isso que"

Emenda de parágrafo que aponta para a própria estrutura do texto em vez de
carregar informação.

> É aqui que a dependência de gente altamente técnica começa a cair.

> É por isso que entramos em operação com histórico.

**Saída:** comece pela informação.

> A dependência de gente altamente técnica começa a cair nesse estágio.

### 8. Triplete nominal

Três substantivos em paralelo com artigo repetido.

> Um indicador, uma definição, um responsável.

**Saída:** dois itens, ou uma frase com verbo.

### 9. Paralelismo mecânico com "cada"

> Cada movimento entre eles é uma cópia, e cada cópia é uma versão do número.

**Saída:** corte o segundo elo. O primeiro já fez o ponto.

### 10. Título de palavras-frase

Três palavras isoladas com ponto, usadas como título ou coluna.

> Fundação. Governança. IA em produção.

**Saída:** uma frase com sujeito e verbo diz mais. Em coluna de layout, aceite
duas palavras no máximo, e só quando o design pedir.

### 11. Pergunta retórica autorrespondida

Faz a pergunta e responde na frase seguinte, simulando um diálogo que não
existe.

> E o custo disso? O custo aparece na decisão errada.

**Saída:** corte a pergunta e deixe a resposta.

**Exceção que o detector respeita:** FAQ. Ali pergunta seguida de resposta é o
formato correto, inclusive para o schema `FAQPage`. O detector ignora o que
está dentro de `<details>` e de seções de FAQ.

---

## Peso 1

### 12. Muleta "vira"

O verbo "virar" como atalho de qualquer transformação.

> Prioridade vira negociação.

> Toda pergunta de negócio vira ticket.

**Saída:** use o verbo específico.

> A prioridade se decide por negociação.

### 13. "em vez de" recorrente

Contraste por substituição usado como fórmula. Uma vez passa. Três na mesma
página é tique.

> pipeline declarativo, com qualidade automatizada, em vez de script que só uma
> pessoa sabe rodar

**Saída:** afirme o que é feito e deixe o contraponto de fora, ou separe em
outra frase.

> Sai de cena o script que só uma pessoa sabe rodar.

---

## Travessão cercado de espaços (peso 2)

O travessão longo (—) com espaço dos dois lados é a marca de IA mais conhecida, porque
quase ninguém digita esse caractere no teclado. Em mensagem, ele denuncia na hora.

> O prazo é curto — mas dá para fazer.

**Saída:** vírgula, ponto ou duas frases.

> O prazo é curto, mas dá para fazer.

---

## Palavra sem acento (peso 3)

"voce", "nao", "tambem" num texto que acentua todo o resto é erro de digitação, e o
leitor percebe. O detector só cobra quando o texto acentua mais do que escorrega:
quem escreve sem acento de propósito (comum no WhatsApp) não é cobrado.

---

## Suas regras

Frase feita, palavra que você não usa, emoji em texto de trabalho: isso varia de
pessoa para pessoa, e por isso mora no `minhas-regras.json`, e não aqui.

---

## Limites do detector

Ele lê texto, Markdown e HTML. Em HTML ignora header, footer, nav e mega-menu, porque
senão um achado de menu apareceria em todas as páginas do site.

Ele acha estrutura, não sentido. Texto vazio e bem escrito passa limpo. E texto
bom pode ser sinalizado: o padrão pode ser exatamente o efeito desejado naquela
frase. O relatório é entrada para decisão humana.

Falsos positivos conhecidos: perguntas de FAQ (já tratado), listas de três itens
em bullet quando o conteúdo realmente tem três itens, e "em vez de" em
comparação técnica legítima.

---

## Afirmação verificável sem fonte (peso 2)

**Marca:** frase com número em %, valor em R$, "nº" de norma, ou o nome de uma lei,
resolução, ato, decreto ou portaria, sem link e sem atribuição ("segundo", "conforme",
"de acordo com", "fonte", "referências") na própria frase, na anterior ou na seguinte.

**Exemplo real** (artigo de reforma tributária, setembro de 2026):

> Em 31 de julho, a Resolução CGIBS nº 14/2026 elevou a estimativa da alíquota conjunta
> de 26,5% para 27,91%.

**Reescrita:** abra a resolução, confira os dois números, e linke na frase.

> Em 31 de julho, a [Resolução CGIBS nº 14/2026](URL-oficial) elevou a estimativa da
> alíquota conjunta de 26,5% para 27,91%.

**Falso positivo conhecido:** a premissa de um exemplo numérico ("os insumos equivalem a
20% da receita") é hipótese, e não afirmação sobre o mundo. Fica, desde que o parágrafo
deixe claro que é exemplo.

