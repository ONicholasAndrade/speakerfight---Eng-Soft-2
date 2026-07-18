# Contribuições dos Integrantes

## 1. Objetivo

Este documento registra as contribuições dos integrantes durante a evolução do projeto **Speakerfight**, desenvolvido como trabalho final da disciplina **Engenharia de Software II (CSI410)**.

A organização do trabalho utilizou:

- issues para registrar funcionalidades e atividades;
- branches específicas para implementação, testes, refatoração e documentação;
- commits descritivos;
- Pull Requests;
- revisões cruzadas;
- testes automatizados antes das integrações;
- uma branch de integração denominada `trabalho-csi410`.

---

## 2. Integrantes

- **Nicholas Andrade**
- **Thiago Ker**

---

## 3. Contribuições de Nicholas Arthur Guimarães Andrade

### 3.1 Issue #304 — Data de abertura para envio de propostas

Nicholas ficou responsável pela implementação da data inicial para o recebimento de propostas em um evento.

Principais atividades:

- análise da Issue #304;
- criação do campo `accept_proposals_at` no Model `Event`;
- configuração do campo como opcional para preservar a compatibilidade com eventos antigos;
- criação da migration `deck/0020_add_accept_proposals_at.py`;
- atualização da interface administrativa;
- criação e execução de testes;
- validação do comportamento da funcionalidade;
- criação da branch `feat/issue-304-opening-date`;
- criação do Pull Request relacionado à Issue #304.

### 3.2 Análise e documentação da arquitetura

Nicholas ficou responsável pela análise da arquitetura do projeto.

Principais atividades:

- identificação do sistema como uma aplicação monolítica;
- identificação do padrão MTV utilizado pelo Django;
- descrição das responsabilidades de Models, Views e Templates;
- análise dos principais módulos da aplicação;
- documentação das relações entre os componentes;
- criação dos diagramas arquiteturais;
- atualização da arquitetura após as Issues #304 e #306;
- criação e atualização de `documentacao/arquitetura.md`;
- submissão do documento para revisão por Pull Request.

### 3.3 Identificação de code smells

Nicholas ficou responsável pela inspeção do código e pela seleção de três ocorrências para refatoração.

Code smells documentados:

1. **Long Method** em `ListEvents.get_queryset()`;
2. **Switch Statement**, representado por uma cadeia de condicionais, em `Proposal.user_can_vote()`;
3. **Long Method e código duplicado** nas ações de votar, aprovar e desaprovar propostas.

A análise também registrou que não foi encontrado um caso tecnicamente defensável de Long Parameter List nos arquivos selecionados.

### 3.4 Refatorações e padrões

Nicholas implementou as refatorações relacionadas aos três code smells.

Principais soluções:

- aplicação de **Extract Method** em `ListEvents`;
- separação da pesquisa, dos filtros e da paginação;
- criação de uma cadeia de regras para `Proposal.user_can_vote()`;
- estrutura inspirada em **Chain of Responsibility**;
- criação da classe-base `ProposalActionView`;
- aplicação do padrão **Template Method**;
- remoção da duplicação dos métodos `dispatch()`;
- aplicação de princípios e boas práticas relacionados a SRP, OCP e DRY.

As alterações foram reunidas no **PR #7**, referente à remoção dos code smells em eventos e propostas.
A documentação final das refatorações, dos padrões e dos code smells foi integrada pelo **PR #10**.

### 3.5 Testes de caracterização e regressão

Antes das refatorações, Nicholas criou testes para registrar o comportamento existente.

Foi criado o arquivo:

```text
deck/tests/test_refactoring.py
```

Cenários cobertos:

- pesquisa de evento pela descrição;
- comportamento da busca com eventos passados;
- página não numérica retornando a primeira página;
- página acima do limite retornando a última página;
- listagem correta de eventos passados;
- pesquisa aplicada somente aos eventos passados quando `past_events=True`.

Também foram executados:

- testes funcionais de eventos;
- testes funcionais de propostas;
- testes dos Models;
- suíte completa do projeto.

### 3.6 Análise de qualidade

Nicholas realizou uma análise comparativa antes e depois das refatorações utilizando o **Radon 4.3.2**.

Métricas avaliadas:

- complexidade ciclomática;
- índice de manutenibilidade;
- LOC;
- LLOC;
- SLOC.

Principais resultados:

- complexidade média reduzida de A (2,34) para A (2,03);
- `ListEvents.get_queryset()` reduzido de B (6) para A (1);
- `Proposal.user_can_vote()` reduzido de B (6) para A (3);
- três métodos `dispatch()` A (5) substituídos por um fluxo comum A (3);
- `views.py` passou de manutenibilidade B (18,88) para A (20,59);
- linhas lógicas totais reduzidas de 667 para 652.

A análise foi registrada em:

```text
documentacao/analise_qualidade.md
```

As evidências foram armazenadas em:

```text
documentacao/evidencias/qualidade/
```

A análise foi inicialmente submetida no PR #8. Como esse PR foi
mesclado em `master`, o conteúdo foi posteriormente integrado à branch
`trabalho-csi410` pelo PR #9.

### 3.7 Documentação

Nicholas ficou responsável ou participou diretamente dos seguintes documentos:

- `documentacao/arquitetura.md`;
- `documentacao/padroes_e_smells.md`;
- `documentacao/analise_qualidade.md`;
- `documentacao/contribuicoes.md`;
- atualização do `README.md`;
- organização das evidências da análise de qualidade.

### 3.8 Participação na apresentação

Nicholas ficou responsável principalmente por apresentar:

- visão geral do Speakerfight;
- arquitetura monolítica e padrão MTV;
- Issue #304;
- identificação dos code smells;
- refatorações aplicadas;
- Template Method;
- cadeia de regras;
- resultados da análise de qualidade;
- comparação antes e depois das alterações.

---

## 4. Contribuições de Thiago

### 4.1 Issue #306 — Restrição de propostas antes da data de abertura

Thiago ficou responsável pela regra que impede o envio de propostas antes da data configurada em `accept_proposals_at`.

Principais atividades:

- análise da Issue #306;
- implementação da propriedade de verificação da data de abertura;
- validação da regra no Model `Proposal`;
- validação na View de criação de propostas;
- criação de mensagens para eventos que ainda não aceitam propostas;
- implementação dos redirecionamentos necessários;
- criação e execução de testes;
- criação da branch `feat/issue-306-restrict-proposals-before-opening-date`;
- criação do Pull Request relacionado à Issue #306.

A implementação foi integrada pelo **PR #2**.

### 4.2 Testes de aceitação

Thiago ficou responsável pelos testes de aceitação do sistema.

A atividade está associada ao **PR #4** e contempla três ou mais cenários executados com Selenium ou Cypress.

Os cenários devem validar, principalmente:

- tentativa de envio antes da abertura;
- envio dentro do período permitido;
- tentativa de envio depois do encerramento;
- mensagens e redirecionamentos apresentados ao usuário.

Os comandos, arquivos e resultados definitivos são documentados em:

```text
documentacao/testes_devops.md
```

### 4.3 Integração contínua

Thiago ficou responsável pela criação e melhoria da integração contínua com GitHub Actions.

A atividade está associada ao **PR #5**.

Principais responsabilidades:

- criação do workflow;
- configuração do ambiente da aplicação;
- instalação das dependências;
- preparação do banco ou serviços necessários;
- execução dos testes automatizados;
- validação dos resultados na aba Actions;
- documentação das etapas da pipeline;
- análise da solução existente e das melhorias realizadas.

### 4.4 Documentação

Thiago ficou responsável ou participou diretamente de:

- informações relacionadas à Issue #306;
- documentação dos testes de aceitação;
- documentação do GitHub Actions;
- criação ou atualização de `documentacao/testes_devops.md`;
- contribuição para o `README.md`;
- registro das evidências de testes e CI.

---

## 5. Revisões cruzadas

Os integrantes realizaram revisões dos Pull Requests um do outro.

### 5.1 Revisões realizadas por Nicholas

Nicholas revisou ou acompanhou principalmente:

- implementação da Issue #306;
- testes da regra de abertura;
- PR #4 de testes de aceitação;
- PR #5 de GitHub Actions;
- documentação relacionada a testes e DevOps;
- integração das alterações em `trabalho-csi410`.

Durante as revisões, foram observados:

- uso correto da regra de negócio;
- preservação da compatibilidade com Python 2.7 e Django legado;
- presença de testes suficientes;
- clareza dos cenários;
- comandos de execução;
- integração dos testes à pipeline;
- ausência de arquivos locais indevidos.

### 5.2 Revisões realizadas por Thiago

Thiago revisou principalmente:

- implementação da Issue #304;
- documentação arquitetural;
- testes de caracterização;
- refatorações do PR #7;
- análise de qualidade do PR #8;
- documentação de padrões e code smells.

Na revisão das refatorações, Thiago sugeriu:

- remoção de duplicação em `get_context_data`;
- renomeação de `filter_events()` para `apply_filters()`;
- documentação da prioridade entre pesquisa e filtros;
- criação de teste específico para pesquisa em eventos passados.

As sugestões foram implementadas antes da aprovação.

### 5.3 Objetivos das revisões

As revisões cruzadas foram utilizadas para:

- localizar erros antes do merge;
- verificar a aderência às Issues;
- solicitar melhorias;
- validar os testes;
- conferir a documentação;
- reduzir o risco de regressões;
- distribuir o conhecimento técnico entre os integrantes.

---

## 6. Issues e Pull Requests relacionados

| Item | Responsável principal | Conteúdo | Situação |
|---|---|---|---|
| Issue #304 | Nicholas | Data inicial para recebimento de propostas | Concluída |
| PR #1 | Nicholas | Implementação de `accept_proposals_at` | Mesclado |
| Issue #306 | Thiago | Restrição de propostas antes da abertura | Concluída |
| PR #2 | Thiago | Implementação da Issue #306 | Mesclado |
| PR #3 | Nicholas | Documentação da arquitetura do Speakerfight | Mesclado |
| PR #4 | Thiago | Testes de aceitação com Selenium | Em andamento |
| PR #5 | Thiago | GitHub Actions e integração contínua | Em andamento |
| PR #6 | Nicholas | Testes de caracterização da listagem | Mesclado |
| PR #7 | Nicholas | Refatorações e remoção de code smells | Mesclado |
| PR #8 | Nicholas | Análise de qualidade com Radon | Mesclado |
| PR #9 | Nicholas | Integração da análise em `trabalho-csi410` | Mesclado |
| PR #10 | Nicholas | Documentação de padrões e code smells | Mesclado |

---

## 7. Divisão do trabalho

| Área | Nicholas | Thiago |
|---|---:|---:|
| Issue #304 | Principal | Revisão |
| Issue #306 | Revisão | Principal |
| Arquitetura | Principal | Revisão |
| Testes de caracterização | Principal | Revisão |
| Code smells e refatorações | Principal | Revisão |
| Padrões de projeto | Principal | Revisão |
| Análise de qualidade | Principal | Revisão |
| Testes de aceitação | Revisão | Principal |
| GitHub Actions | Revisão | Principal |
| Documentação de testes e DevOps | Colaboração | Principal |
| README | Colaboração | Colaboração |
| Validação final | Colaboração | Colaboração |

---

## 8. Estratégia de desenvolvimento

A branch de integração utilizada foi:

```text
trabalho-csi410
```

Exemplos de branches de trabalho:

- `feat/issue-304-opening-date`;
- `feat/issue-306-restrict-proposals-before-opening-date`;
- `test/refactoring-characterization`;
- `refactor/list-events-long-method`;
- `docs/arquitetura`;
- `docs/analise-qualidade`;
- `docs/padroes-e-smells`;
- `docs/contribuicoes`.

O fluxo adotado foi:

1. atualizar `trabalho-csi410`;
2. criar uma branch específica;
3. implementar a atividade;
4. executar os testes;
5. realizar o commit;
6. enviar a branch ao GitHub;
7. abrir um Pull Request;
8. solicitar a revisão do outro integrante;
9. corrigir os apontamentos;
10. realizar o merge após aprovação.

---

## 9. Participação conjunta

Apesar da divisão de responsabilidades, algumas atividades foram realizadas em conjunto:

- definição do escopo do trabalho;
- escolha das Issues;
- discussão das regras de negócio;
- revisão das alterações;
- execução de testes;
- organização dos documentos;
- verificação dos links;
- atualização do README;
- limpeza do repositório;
- validação final do projeto.

---

## 10. Resumo final

| Integrante | Principais responsabilidades |
|---|---|
| Nicholas Arthur Guimarães Andrade | Issue #304, arquitetura, testes de caracterização, code smells, refatorações, padrões de projeto, análise de qualidade e documentação relacionada |
| Thiago | Issue #306, testes de aceitação, GitHub Actions, documentação de testes e DevOps |
| Ambos | Revisões cruzadas, README, testes finais, validação dos PRs, organização da entrega|

