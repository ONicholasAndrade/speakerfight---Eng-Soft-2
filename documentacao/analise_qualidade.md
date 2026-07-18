# Análise de Qualidade de Código

## 1. Objetivo

Este documento apresenta uma análise comparativa da qualidade do código antes e depois das refatorações realizadas nos arquivos `deck/views.py` e `deck/models.py` do projeto Speakerfight.

A análise tem como objetivos:

- verificar o impacto das refatorações sobre a complexidade ciclomática;
- comparar o índice de manutenibilidade dos arquivos;
- analisar a variação das métricas de linhas;
- registrar evidências quantitativas das melhorias realizadas;
- confirmar que as alterações estruturais preservaram o comportamento existente.

---

## 2. Escopo da análise

Foram analisados os arquivos:

- `deck/views.py`;
- `deck/models.py`.

A comparação foi realizada entre os seguintes commits:

| Versão | Commit |
|---|---|
| Antes das refatorações | `cfb9570` |
| Depois das refatorações | `2d0f08a191d31cfb4642878d0b296b31b1a255aa` |

O commit anterior representa o código antes do tratamento dos code smells escolhidos. O commit posterior contém as refatorações aplicadas em eventos e propostas.

---

## 3. Ferramenta utilizada

Foi utilizado o **Radon 4.3.2**, executado no contêiner Docker do projeto com Python 2.7.

O Radon foi escolhido por permitir a análise estática de código Python e por oferecer compatibilidade com a versão legada utilizada pelo Speakerfight.

As seguintes métricas foram analisadas:

- **Complexidade ciclomática:** mede a quantidade de caminhos independentes existentes no fluxo de execução de funções, métodos e classes.
- **Índice de manutenibilidade:** combina características como volume, complexidade e quantidade de linhas para indicar a facilidade de manutenção do código.
- **Métricas brutas:** apresentam valores como LOC, LLOC, SLOC, comentários e linhas em branco.

### 3.1 Comandos utilizados

Complexidade ciclomática:

```bash
radon cc .quality-analysis/antes/views.py .quality-analysis/antes/models.py -s -a
radon cc .quality-analysis/depois/views.py .quality-analysis/depois/models.py -s -a
```

Índice de manutenibilidade:

```bash
radon mi .quality-analysis/antes/views.py .quality-analysis/antes/models.py -s
radon mi .quality-analysis/depois/views.py .quality-analysis/depois/models.py -s
```

Métricas de linhas:

```bash
radon raw .quality-analysis/antes/views.py .quality-analysis/antes/models.py -s
radon raw .quality-analysis/depois/views.py .quality-analysis/depois/models.py -s
```

---

## 4. Code smells e refatorações avaliadas

Foram tratados três pontos principais.

| Local | Code smell | Refatoração ou solução |
|---|---|---|
| `ListEvents.get_queryset()` | Long Method | Extract Method |
| `Proposal.user_can_vote()` | Switch Statement representado por cadeia de condicionais | Cadeia de regras inspirada em Chain of Responsibility |
| `RateProposal.dispatch()` e métodos semelhantes | Long Method e código duplicado | Classe-base com Template Method |

---

## 5. Complexidade ciclomática

### 5.1 Comparação dos principais elementos

| Elemento analisado | Antes | Depois | Resultado |
|---|---:|---:|---|
| `ListEvents.get_queryset()` | B (6) | A (1) | Complexidade reduzida |
| `Proposal.user_can_vote()` | B (6) | A (3) | Complexidade reduzida |
| `RateProposal.dispatch()` | A (5) | Removido | Fluxo centralizado |
| `ApproveProposal.dispatch()` | A (5) | Removido | Fluxo centralizado |
| `DisapproveProposal.dispatch()` | A (5) | Removido | Fluxo centralizado |
| `ProposalActionView.dispatch()` | Inexistente | A (3) | Fluxo compartilhado |
| `ListEvents.apply_filters()` | Inexistente | A (4) | Regras de filtragem separadas |
| `ListEvents.paginate_events()` | Inexistente | A (3) | Paginação isolada |

### 5.2 Complexidade média

| Métrica | Antes | Depois |
|---|---:|---:|
| Blocos analisados | 103 | 119 |
| Complexidade média | A (2,34) | A (2,03) |

A quantidade de blocos aumentou de 103 para 119 porque métodos longos foram divididos em métodos menores e novas abstrações foram criadas.

Apesar desse aumento, a complexidade média diminuiu de aproximadamente 2,34 para 2,03. Portanto, o código passou a possuir mais unidades pequenas, porém cada unidade ficou, em média, mais simples.

---

## 6. Análise das refatorações

### 6.1 `ListEvents.get_queryset()`

Antes da refatoração, o método `get_queryset()` concentrava diferentes responsabilidades:

- obtenção do queryset;
- filtragem de eventos publicados;
- filtragem de eventos futuros e passados;
- leitura do critério de pesquisa;
- pesquisa por título e descrição;
- criação da paginação;
- tratamento de página não numérica;
- tratamento de página fora do intervalo.

Foi aplicada a técnica **Extract Method**, distribuindo essas responsabilidades entre:

- `apply_filters()`;
- `filter_past_events()`;
- `get_search_criteria()`;
- `filter_by_search()`;
- `paginate_events()`.

Também foi criado o atributo:

```python
events_per_page = 15
```

Esse atributo substituiu o valor fixo utilizado diretamente no `Paginator`.

A complexidade de `ListEvents.get_queryset()` foi reduzida de **B (6)** para **A (1)**. A classe `ListEvents` também passou de complexidade **A (5)** para **A (2)**.

A lógica não foi removida, mas distribuída em métodos menores e com responsabilidades mais claras. O método `apply_filters()` ficou com complexidade A (4), enquanto os métodos auxiliares mais simples ficaram com complexidade A (1).

### 6.2 `Proposal.user_can_vote()`

Antes da refatoração, `Proposal.user_can_vote()` utilizava uma cadeia de condicionais para decidir se um usuário poderia votar.

As condições avaliavam:

1. se o usuário era o autor da própria proposta;
2. se a votação pública estava habilitada;
3. se o usuário era superusuário;
4. se o usuário participava do júri.

A lógica foi dividida em regras independentes:

- `_deny_proposal_author_vote()`;
- `_allow_public_vote()`;
- `_allow_superuser_vote()`;
- `_allow_jury_vote()`.

O método `get_voting_rules()` passou a fornecer a ordem das regras, enquanto `user_can_vote()` percorre essa sequência até encontrar uma decisão.

Essa estrutura forma uma cadeia de regras inspirada no padrão **Chain of Responsibility**, pois cada regra pode tomar uma decisão ou permitir que a próxima seja avaliada.

A complexidade de `Proposal.user_can_vote()` foi reduzida de **B (6)** para **A (3)**.

### 6.3 Ações sobre propostas

Antes da refatoração, as classes:

- `RateProposal`;
- `ApproveProposal`;
- `DisapproveProposal`;

possuíam métodos `dispatch()` muito semelhantes. Cada método repetia o mesmo fluxo:

1. obter a proposta;
2. verificar se o usuário estava autenticado;
3. verificar a permissão específica;
4. criar mensagem de erro;
5. redirecionar requisições GET;
6. criar resposta JSON para requisições POST;
7. retornar status HTTP 401 quando necessário.

Os três métodos possuíam complexidade **A (5)**.

Foi criada a classe-base `ProposalActionView`, que centraliza o fluxo comum no método `dispatch()`.

Cada subclasse passou a implementar somente:

```python
def user_has_permission(self, proposal):
    ...
```

A classe-base define o esqueleto do processo, e as subclasses fornecem a etapa variável de autorização. Essa estrutura corresponde ao padrão **Template Method**.

Os três métodos duplicados foram substituídos por:

- `ProposalActionView.dispatch()` — A (3);
- `RateProposal.user_has_permission()` — A (1);
- `ApproveProposal.user_has_permission()` — A (1);
- `DisapproveProposal.user_has_permission()` — A (1).

O resultado foi a eliminação da duplicação e a centralização das regras comuns de autenticação e resposta.

---

## 7. Índice de manutenibilidade

| Arquivo | Antes | Depois | Resultado |
|---|---:|---:|---|
| `views.py` | B (18,88) | A (20,59) | Melhorou de classificação |
| `models.py` | A (24,43) | A (22,82) | Permaneceu na classificação A |

### 7.1 `views.py`

O índice de manutenibilidade do arquivo `views.py` passou de **B (18,88)** para **A (20,59)**.

Essa melhoria é coerente com:

- redução da complexidade de `ListEvents.get_queryset()`;
- remoção dos três métodos `dispatch()` duplicados;
- centralização do fluxo em `ProposalActionView`;
- diminuição da quantidade de instruções lógicas no arquivo.

### 7.2 `models.py`

O índice de `models.py` passou de **A (24,43)** para **A (22,82)**.

Houve uma pequena redução numérica, mas o arquivo permaneceu na classificação A.

Essa variação não invalida a refatoração. A separação de `user_can_vote()` em vários métodos auxiliares aumentou o volume estrutural do arquivo. Ao mesmo tempo, a complexidade do método principal caiu de B (6) para A (3), deixando as regras mais explícitas e isoladas.

Portanto, a conclusão correta é que o arquivo manteve uma classificação alta de manutenibilidade e reduziu a complexidade concentrada da regra de votação.

---

## 8. Métricas de linhas

### 8.1 Comparação total

| Métrica total | Antes | Depois | Variação |
|---|---:|---:|---:|
| LOC | 1011 | 1130 | +119 |
| LLOC | 667 | 652 | -15 |
| SLOC | 827 | 891 | +64 |
| Linhas em branco | 174 | 229 | +55 |
| Comentários | 10 | 10 | Sem alteração |

### 8.2 Métricas por arquivo

| Arquivo | Métrica | Antes | Depois | Variação |
|---|---|---:|---:|---:|
| `views.py` | LOC | 567 | 657 | +90 |
| `views.py` | LLOC | 380 | 352 | -28 |
| `views.py` | SLOC | 474 | 520 | +46 |
| `models.py` | LOC | 444 | 473 | +29 |
| `models.py` | LLOC | 287 | 300 | +13 |
| `models.py` | SLOC | 353 | 371 | +18 |

### 8.3 Interpretação

**LOC** representa o total de linhas físicas, incluindo código, comentários e linhas em branco.

**LLOC** representa a quantidade de linhas lógicas, associadas às instruções efetivamente executadas.

**SLOC** representa as linhas físicas de código-fonte.

O total de LOC aumentou porque:

- métodos longos foram divididos;
- novas abstrações foram criadas;
- as regras passaram a possuir métodos próprios;
- os blocos foram separados visualmente;
- aumentou a quantidade de linhas em branco entre métodos e classes.

Entretanto, a quantidade total de linhas lógicas diminuiu de 667 para 652, uma redução aproximada de 2,2%.

No arquivo `views.py`, o LLOC caiu de 380 para 352. A redução está relacionada principalmente à remoção dos três métodos `dispatch()` duplicados e à centralização do fluxo em `ProposalActionView`.

No arquivo `models.py`, o LLOC aumentou de 287 para 300 porque a cadeia condicional foi transformada em regras explícitas e independentes. Mesmo com o aumento de linhas, a complexidade de `user_can_vote()` caiu de B (6) para A (3).

Assim, o aumento de linhas físicas não representa aumento direto de complexidade. O código passou a possuir mais métodos pequenos e responsabilidades explícitas, enquanto a complexidade média diminuiu.

---

## 9. Validação por testes

Antes das refatorações, foram adicionados testes de caracterização para registrar o comportamento existente da listagem de eventos.

Os cenários protegidos incluem:

- pesquisa de evento pela descrição;
- comportamento atual da pesquisa com eventos passados;
- página não numérica retornando a primeira página;
- página acima do limite retornando a última página;
- listagem correta de eventos passados;
- pesquisa aplicada sobre eventos passados quando `past_events=True`.

Também foram utilizados os testes funcionais existentes para validar:

- listagem de eventos futuros;
- listagem de eventos passados;
- paginação;
- votação de propostas;
- autenticação;
- autorização;
- aprovação e desaprovação de propostas;
- respostas GET e POST.

Após as refatorações, os testes de caracterização, os testes funcionais e a suíte completa foram executados com sucesso.

Esse resultado indica que as alterações modificaram a estrutura interna do código sem alterar o comportamento funcional esperado.

---

## 10. Resultados consolidados

Os principais resultados foram:

- complexidade média reduzida de **A (2,34)** para **A (2,03)**;
- `ListEvents.get_queryset()` reduzido de **B (6)** para **A (1)**;
- `Proposal.user_can_vote()` reduzido de **B (6)** para **A (3)**;
- três métodos `dispatch()` de complexidade **A (5)** substituídos por um método compartilhado de complexidade **A (3)**;
- índice de manutenibilidade de `views.py` elevado de **B (18,88)** para **A (20,59)**;
- `models.py` mantido na classificação **A**;
- linhas lógicas totais reduzidas de **667** para **652**;
- testes automatizados mantidos aprovados.

---

## 11. Limitações da análise

As métricas do Radon auxiliam na avaliação da estrutura do código, mas não devem ser interpretadas isoladamente.

Uma redução de complexidade não garante, por si só, que o código esteja correto. Da mesma forma, um aumento de LOC não significa necessariamente piora, pois pode resultar da criação de abstrações e da separação de responsabilidades.

Por isso, os resultados quantitativos foram analisados em conjunto com:

- revisão do código;
- identificação dos code smells;
- aplicação das refatorações;
- execução dos testes automatizados;
- preservação das regras de negócio.

A análise ficou restrita aos arquivos `deck/views.py` e `deck/models.py`, pois eles contêm os três pontos escolhidos para refatoração.

---

## 12. Conclusão

A análise indica que as refatorações atingiram o objetivo de reduzir a complexidade concentrada e eliminar duplicação.

A técnica Extract Method reduziu significativamente a complexidade de `ListEvents.get_queryset()`. A cadeia de regras tornou as permissões de votação mais explícitas. A criação de `ProposalActionView` removeu a duplicação existente nas ações de votar, aprovar e desaprovar propostas.

O arquivo `views.py` passou da classificação B para A no índice de manutenibilidade. O arquivo `models.py` permaneceu na classificação A e apresentou redução da complexidade no método escolhido.

Embora LOC e SLOC tenham aumentado, o número de linhas lógicas diminuiu e a complexidade média foi reduzida. Isso mostra que o código ficou mais distribuído em unidades menores e mais simples.

Como a suíte de testes permaneceu aprovada, há evidência de que o comportamento existente foi preservado durante as mudanças estruturais.

---

## 13. Evidências

Os relatórios completos gerados pelo Radon estão armazenados em:

- `documentacao/evidencias/qualidade/commits_analisados.txt`;
- `documentacao/evidencias/qualidade/antes_complexidade.txt`;
- `documentacao/evidencias/qualidade/depois_complexidade.txt`;
- `documentacao/evidencias/qualidade/antes_manutencao.txt`;
- `documentacao/evidencias/qualidade/depois_manutencao.txt`;
- `documentacao/evidencias/qualidade/antes_linhas.txt`;
- `documentacao/evidencias/qualidade/depois_linhas.txt`.
