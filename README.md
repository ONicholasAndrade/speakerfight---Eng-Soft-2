# Speakerfight — Trabalho de Engenharia de Software II

Fork acadêmico do projeto open source [Speakerfight](https://github.com/luanfonceca/speakerfight), utilizado no trabalho prático da disciplina **CSI410 — Engenharia de Software II**, da Universidade Federal de Ouro Preto.

O Speakerfight é uma aplicação web para criação de eventos, submissão de propostas de palestras, votação e organização da programação.

## 1. Objetivo do trabalho

O trabalho teve como objetivo aplicar práticas de engenharia de software em um projeto real, incluindo:

- análise de arquitetura;
- manutenção evolutiva e corretiva;
- identificação e remoção de code smells;
- aplicação de princípios SOLID e padrões de projeto;
- testes automatizados;
- análise de qualidade;
- integração contínua com GitHub Actions;
- organização do desenvolvimento por branches e Pull Requests.

## 2. Repositórios

- **Projeto original:** [luanfonceca/speakerfight](https://github.com/luanfonceca/speakerfight)
- **Fork do trabalho:** [ONicholasAndrade/speakerfight---Eng-Soft-2](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2)

## 3. Integrantes

- **Nicholas Arthur**
- **Thiago Ker**

As responsabilidades detalhadas estão registradas em [`documentacao/contribuicoes.md`](documentacao/contribuicoes.md).

## 4. Tecnologias

- Python 2.7;
- Django 1.11.12;
- SQLite no ambiente de testes;
- Selenium 3.141.0;
- Google Chrome em modo headless;
- Docker e Docker Compose;
- Git e GitHub;
- GitHub Actions;
- Radon para análise de qualidade;
- Mermaid para modelagem da arquitetura.

## 5. Contribuições principais

### 5.1 Issue #304 — Data de abertura das propostas

Foi adicionado ao modelo `Event` o campo:

```python
accept_proposals_at = models.DateTimeField(null=True, blank=True)
```

A alteração permite definir a data e o horário em que um evento começa a receber propostas.

Principais entregas:

- novo campo no modelo;
- migração `deck/0020_add_accept_proposals_at.py`;
- exibição no formulário e no painel administrativo;
- testes de modelo e integridade;
- manutenção da compatibilidade com eventos antigos, pois o campo aceita valor nulo.

Issue original: [#304 — Opening date for proposals](https://github.com/luanfonceca/speakerfight/issues/304)

### 5.2 Issue #306 — Restrição antes da abertura

A regra de criação de propostas foi atualizada para impedir submissões antes de `accept_proposals_at`.

A validação foi aplicada em mais de uma camada:

- propriedade de domínio no modelo `Event`;
- validação no método `Proposal.save`;
- verificação na view de criação;
- mensagens e redirecionamentos;
- testes automatizados.

Issue original: [#306](https://github.com/luanfonceca/speakerfight/issues/306)

## 6. Arquitetura

O Speakerfight possui implantação monolítica e utiliza a arquitetura **MTV — Model, Template e View**, adotada pelo Django.

A análise inclui:

- responsabilidades dos módulos;
- organização dos pacotes;
- relação entre Models, Views, Templates e URLs;
- dependências entre os principais componentes;
- diagrama em Mermaid.

Documento completo: [`documentacao/arquitetura.md`](documentacao/arquitetura.md)

## 7. Code smells, refatorações e padrões

Foram analisados e tratados três pontos principais.

### 7.1 Long Method na listagem de eventos

O método `ListEvents.get_queryset()` concentrava filtros, pesquisa, ordenação e paginação.

A lógica foi separada em métodos menores, incluindo:

- aplicação de filtros;
- pesquisa;
- tratamento de eventos passados;
- paginação.

A técnica principal utilizada foi **Extract Method**.

### 7.2 Regras condicionais de votação

O método `Proposal.user_can_vote()` concentrava várias verificações condicionais.

As regras foram reorganizadas em uma cadeia ordenada de funções, inspirada no padrão **Chain of Responsibility**.

### 7.3 Duplicação em ações sobre propostas

As views de aprovação, reprovação e avaliação possuíam fluxos repetidos.

Foi criada a classe-base `ProposalActionView`, utilizando **Template Method** para centralizar o fluxo comum e permitir que as subclasses definam apenas as partes específicas.

Documento completo: [`documentacao/padroes_e_smells.md`](documentacao/padroes_e_smells.md)

## 8. Testes automatizados

A suíte combina:

- testes unitários;
- testes de integridade dos modelos;
- testes funcionais;
- testes de caracterização;
- testes de aceitação com o cliente interno do Django;
- testes de aceitação com Selenium e Google Chrome.

### 8.1 Testes de caracterização

Antes das refatorações, foram criados testes para preservar o comportamento existente da listagem de eventos.

Arquivo:

```text
deck/tests/test_refactoring.py
```

Os cenários verificam pesquisa, eventos passados e paginação.

### 8.2 Testes de aceitação da janela de propostas

Arquivos:

```text
acceptance_tests/test_proposal_window.py
acceptance_tests/test_proposal_window_selenium.py
```

Os três cenários principais são:

1. bloquear a criação antes da data de abertura;
2. permitir a criação durante o período válido;
3. bloquear a criação após a data de encerramento.

Os testes Selenium utilizam:

- `StaticLiveServerTestCase`;
- Selenium Server;
- ChromeDriver;
- Google Chrome em modo headless;
- Docker Compose.

O cenário de criação também interage com o editor TinyMCE utilizado pelo formulário.

## 9. Execução da suíte completa

### 9.1 Requisitos

- Git;
- Docker;
- Docker Compose.

### 9.2 Executar os testes

Na raiz do repositório:

```bash
docker compose -f docker-compose.acceptance.yml up \
  --build \
  --force-recreate \
  --abort-on-container-exit \
  --exit-code-from web
```

O comando:

1. constrói a imagem do projeto;
2. instala as dependências;
3. inicia o Selenium Server e o Chrome;
4. executa `python manage.py check`;
5. executa toda a suíte com `python manage.py test -v 2`;
6. retorna o código de saída do serviço `web`.

### 9.3 Limpar o ambiente

```bash
docker compose -f docker-compose.acceptance.yml down \
  --volumes \
  --remove-orphans
```

### 9.4 Resultado local

Execução realizada em 18 de julho de 2026:

```text
Ran 250 tests in 6.652s

OK
System check identified no issues (0 silenced).
```

Resultado:

```text
250 testes executados
250 testes aprovados
0 falhas
0 erros
```

Mais informações: [`documentacao/testes_devops.md`](documentacao/testes_devops.md)

## 10. Integração contínua

O workflow está em:

```text
.github/workflows/ci.yml
```

Nome:

```text
Django and Selenium Tests
```

O GitHub Actions é acionado em Pull Requests e pushes destinados às branches:

- `master`;
- `trabalho-csi410`.

A pipeline:

1. faz checkout do repositório;
2. valida o arquivo `docker-compose.acceptance.yml`;
3. constrói as imagens;
4. inicia Django, Selenium Server e Chrome;
5. executa o system check do Django;
6. executa toda a suíte automatizada;
7. usa o resultado do serviço `web` como resultado do workflow;
8. remove containers, redes e volumes com `if: always()`.

## 11. Análise de qualidade

A análise foi realizada com o Radon, comparando o código antes e depois das refatorações.

Principais resultados:

- complexidade média: **A 2,3398 → A 2,0336**;
- `ListEvents.get_queryset`: **B6 → A1**;
- `Proposal.user_can_vote`: **B6 → A3**;
- índice de manutenibilidade de `deck/views.py`: **B 18,88 → A 20,59**;
- métodos longos foram divididos em unidades menores;
- duplicações nas ações de propostas foram centralizadas.

Documento completo: [`documentacao/analise_qualidade.md`](documentacao/analise_qualidade.md)

## 12. Documentação

| Documento | Conteúdo |
|---|---|
| [`arquitetura.md`](documentacao/arquitetura.md) | Arquitetura MTV, componentes e diagrama |
| [`padroes_e_smells.md`](documentacao/padroes_e_smells.md) | Code smells, refatorações e padrões |
| [`analise_qualidade.md`](documentacao/analise_qualidade.md) | Métricas e comparação com Radon |
| [`testes_devops.md`](documentacao/testes_devops.md) | Testes, Selenium, Docker e GitHub Actions |
| [`contribuicoes.md`](documentacao/contribuicoes.md) | Issues, Pull Requests e responsabilidades |

As evidências da análise de qualidade estão em:

```text
documentacao/evidencias/qualidade/
```

## 13. Pull Requests

| PR | Conteúdo | Situação |
|---|---|---|
| [#1](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/1) | Campo de abertura das propostas — Issue #304 | Mesclado |
| [#2](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/2) | Restrição antes da abertura — Issue #306 | Mesclado |
| [#3](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/3) | Documentação da arquitetura | Mesclado |
| [#4](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/4) | Testes de aceitação iniciais | Mesclado |
| [#5](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/5) | Workflow inicial do GitHub Actions | Mesclado |
| [#6](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/6) | Testes de caracterização | Mesclado |
| [#7](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/7) | Refatorações e remoção de code smells | Mesclado |
| [#8](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/8) | Análise de qualidade | Mesclado em `master` |
| [#9](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/9) | Integração da análise de qualidade na branch de trabalho | Mesclado |
| [#10](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/10) | Padrões e code smells | Mesclado |
| [#11](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/11) | Registro das contribuições | Mesclado |
| [#12](https://github.com/ONicholasAndrade/speakerfight---Eng-Soft-2/pull/12) | Integração dos testes de aceitação em `master` | Mesclado |

A relação detalhada de responsabilidades e revisões está em [`documentacao/contribuicoes.md`](documentacao/contribuicoes.md).

## 14. Fluxo de branches

Durante o desenvolvimento, a branch principal de integração foi:

```text
trabalho-csi410
```

As atividades foram desenvolvidas em branches específicas e integradas por Pull Requests.

Depois da consolidação em `master`, a complementação dos testes Selenium, da suíte completa, do CI e da documentação foi desenvolvida em:

```text
test/selenium-e-documentacao-devops
```

## 15. Estrutura relevante

```text
.github/
└── workflows/
    └── ci.yml

acceptance_tests/
├── test_proposal_window.py
├── test_proposal_window_selenium.py
└── test_server.sh

deck/
├── migrations/
│   └── 0020_add_accept_proposals_at.py
└── tests/
    └── test_refactoring.py

documentacao/
├── analise_qualidade.md
├── arquitetura.md
├── contribuicoes.md
├── padroes_e_smells.md
├── testes_devops.md
└── evidencias/
    └── qualidade/

docker-compose.acceptance.yml
README.md
```

## 16. Projeto original

O código-base e a identidade visual pertencem ao projeto open source Speakerfight.

- Repositório original: [luanfonceca/speakerfight](https://github.com/luanfonceca/speakerfight)
- Guia de contribuição original: [CONTRIBUTING.md](CONTRIBUTING.md)
- Licença: [MIT](LICENSE)
