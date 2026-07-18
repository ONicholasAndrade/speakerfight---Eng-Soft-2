# Testes de Software e Práticas DevOps

## 1. Objetivo

Este documento apresenta a estratégia de testes automatizados e as práticas de
integração contínua aplicadas ao projeto Speakerfight durante o trabalho de
Engenharia de Software II.

Os testes desenvolvidos validam a regra de negócio relacionada ao período de
recebimento de propostas de um evento.

A funcionalidade considera três situações:

1. antes da data de abertura, novas propostas devem ser bloqueadas;
2. durante o período válido, novas propostas devem ser permitidas;
3. depois da data de encerramento, novas propostas devem ser bloqueadas.

Além dos testes utilizando o cliente interno do Django, foram implementados
testes funcionais com Selenium, executados em um navegador Google Chrome real
dentro de um container Docker.

---

## 2. Tecnologias utilizadas

As principais tecnologias utilizadas nos testes e na integração contínua foram:

- Python 2.7;
- Django 1.11.12;
- `django.test.TestCase`;
- `StaticLiveServerTestCase`;
- Selenium 3.141.0;
- Google Chrome em modo headless;
- Docker;
- Docker Compose;
- GitHub Actions.

A imagem utilizada para o navegador é:

```text
selenium/standalone-chrome:3.141.59-20210929
```

Essa versão foi utilizada por ser compatível com o Selenium 3.141.0 e com o
ambiente legado do projeto.

---

## 3. Organização dos testes

Os testes relacionados à janela de propostas estão distribuídos nos seguintes
arquivos:

```text
acceptance_tests/test_proposal_window.py
acceptance_tests/test_proposal_window_selenium.py
```

O arquivo `test_proposal_window.py` valida a regra de negócio utilizando o
cliente de testes do Django.

O arquivo `test_proposal_window_selenium.py` valida os mesmos cenários por meio
de um navegador Chrome controlado pelo Selenium.

O servidor Django utilizado pelos testes Selenium é iniciado com
`StaticLiveServerTestCase`, enquanto o Chrome é executado em um container
separado.

---

## 4. Cenários de aceitação

### 4.1 Cenário 1 — Bloquear proposta antes da abertura

```gherkin
Funcionalidade: Controle do período de recebimento de propostas

Cenário: Usuário tenta enviar uma proposta antes da abertura
  Dado que existe um evento com a abertura de propostas definida para uma data futura
  E que o usuário está autenticado
  Quando o usuário acessa a página de criação de proposta
  Então o sistema deve redirecioná-lo para a página do evento
  E deve informar que o evento ainda não está recebendo propostas
  E nenhuma proposta deve ser criada
```

Teste Selenium correspondente:

```text
test_browser_blocks_proposal_before_opening_date
```

O teste cria um evento cuja data `accept_proposals_at` ainda não foi alcançada.
O navegador tenta acessar a página de criação de propostas e verifica a
mensagem:

```text
This Event doesn't accept Proposals yet.
```

Também é verificado que nenhuma proposta foi registrada no banco de dados.

---

### 4.2 Cenário 2 — Permitir proposta durante o período válido

```gherkin
Funcionalidade: Controle do período de recebimento de propostas

Cenário: Usuário envia uma proposta durante o período permitido
  Dado que existe um evento cuja abertura de propostas já ocorreu
  E cuja data de encerramento ainda não foi alcançada
  E que o usuário está autenticado
  Quando o usuário acessa o formulário de criação de proposta
  E preenche o título e a descrição
  E envia o formulário
  Então a proposta deve ser criada
  E o título da proposta deve ser exibido na página do evento
```

Teste Selenium correspondente:

```text
test_browser_creates_proposal_during_valid_period
```

O Selenium acessa o formulário, preenche o título e a descrição da proposta e
envia os dados pelo navegador.

Como o campo de descrição utiliza um editor TinyMCE, o teste aguarda a
inicialização do editor, define seu conteúdo e sincroniza o valor com o campo
que será enviado ao Django.

Ao final, o teste confirma:

- o redirecionamento para a página do evento;
- a exibição do título da proposta;
- a existência da proposta no banco de dados.

---

### 4.3 Cenário 3 — Bloquear proposta depois do encerramento

```gherkin
Funcionalidade: Controle do período de recebimento de propostas

Cenário: Usuário tenta enviar uma proposta depois do encerramento
  Dado que existe um evento cuja data de encerramento já passou
  E que o usuário está autenticado
  Quando o usuário acessa a página de criação de proposta
  Então o sistema deve redirecioná-lo para a página do evento
  E deve informar que o evento não recebe mais propostas
  E nenhuma proposta deve ser criada
```

Teste Selenium correspondente:

```text
test_browser_blocks_proposal_after_closing_date
```

O teste cria um evento cuja data `closing_date` já passou e verifica a mensagem:

```text
This Event doesn't accept Proposals anymore.
```

Também é confirmado que nenhuma proposta foi salva.

---

## 5. Autenticação utilizada nos testes Selenium

Durante a preparação do teste, o usuário é criado pelo Django e autenticado pelo
cliente de testes.

O cookie da sessão autenticada é transferido para o navegador controlado pelo
Selenium.

Essa abordagem permite concentrar o teste na funcionalidade analisada: o
controle temporal da criação de propostas.

Depois da autenticação, todas as ações da funcionalidade são executadas por um
navegador real, incluindo:

- acesso às páginas;
- leitura das mensagens;
- preenchimento dos campos;
- envio do formulário;
- acompanhamento dos redirecionamentos.

---

## 6. Execução local

### 6.1 Requisitos

Para executar os testes, é necessário ter instalado:

- Git;
- Docker;
- Docker Compose.

Não é necessário instalar manualmente Python, Django, Selenium ou Chrome, pois
essas dependências são preparadas pelos containers.

### 6.2 Comando de execução

Na raiz do projeto, execute:

```bash
docker compose -f docker-compose.acceptance.yml up \
  --build \
  --force-recreate \
  --abort-on-container-exit \
  --exit-code-from web
```

Esse comando realiza as seguintes etapas:

1. constrói a imagem do projeto;
2. instala as dependências Python;
3. inicia o Selenium Server;
4. inicia o Chrome em modo headless;
5. executa o `manage.py check`;
6. cria o banco de dados de testes;
7. executa toda a suíte automatizada;
8. encerra os containers ao terminar.

### 6.3 Limpeza do ambiente

Após a execução, os containers e volumes podem ser removidos com:

```bash
docker compose -f docker-compose.acceptance.yml down \
  --volumes \
  --remove-orphans
```

---

## 7. Suíte completa

O script responsável pela execução é:

```text
acceptance_tests/test_server.sh
```

Seu conteúdo principal é:

```bash
python manage.py check
python manage.py test -v 2
```

O comando `python manage.py test` foi utilizado para executar toda a suíte
descoberta pelo Django, em vez de limitar a validação a apenas alguns módulos.

A execução local realizada em 18 de julho de 2026 apresentou o seguinte
resultado:

```text
Ran 250 tests in 6.652s

OK
System check identified no issues (0 silenced).
```

Portanto, os 250 testes automatizados foram aprovados, incluindo os três
cenários executados com Selenium.

Os avisos relacionados ao `psycopg2` e a datas sem informação de fuso horário
não interromperam a execução e não representaram falhas na suíte.

---

## 8. Ambiente Docker para os testes

O arquivo utilizado para orquestrar o ambiente é:

```text
docker-compose.acceptance.yml
```

Ele possui dois serviços principais.

### Serviço `selenium`

Responsável por executar:

- Selenium Server;
- ChromeDriver;
- Google Chrome em modo headless.

### Serviço `web`

Responsável por:

- construir o projeto com Python 2.7;
- instalar as dependências;
- executar o Django;
- iniciar o servidor de testes;
- executar o `manage.py check`;
- executar toda a suíte automatizada.

As variáveis utilizadas para a comunicação entre os serviços são:

```text
SELENIUM_URL=http://selenium:4444/wd/hub
SELENIUM_BROWSER_URL=http://web:8081
```

---

## 9. Análise da integração contínua

O projeto já possuía testes automatizados, mas a execução inicial do workflow
era limitada a módulos específicos.

A melhoria implementada passou a executar:

```bash
python manage.py test -v 2
```

Dessa maneira, todos os testes encontrados pelo Django são executados.

Também foi adicionada ao CI a infraestrutura necessária para executar os testes
Selenium em um navegador real.

---

## 10. Pipeline do GitHub Actions

O workflow está localizado em:

```text
.github/workflows/ci.yml
```

Nome do workflow:

```text
Django and Selenium Tests
```

O workflow é executado em:

- Pull Requests destinados à branch `master`;
- Pull Requests destinados à branch `trabalho-csi410`;
- pushes realizados em `master`;
- pushes realizados em `trabalho-csi410`.

A pipeline realiza as seguintes etapas:

1. obtém o código do repositório;
2. valida o arquivo `docker-compose.acceptance.yml`;
3. constrói as imagens Docker;
4. inicia o Django e o Selenium;
5. executa o `manage.py check`;
6. executa toda a suíte automatizada;
7. utiliza o código de saída do serviço `web` como resultado do CI;
8. remove containers, redes e volumes mesmo em caso de falha.

O comando principal executado no GitHub Actions é:

```bash
docker compose -f docker-compose.acceptance.yml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from web
```

A limpeza do ambiente é garantida pelo uso de:

```yaml
if: always()
```

Assim, os containers são removidos tanto após execuções aprovadas quanto após
falhas.

---

## 11. Melhorias DevOps implementadas

As principais melhorias aplicadas foram:

- criação de uma pipeline automatizada no GitHub Actions;
- execução do `manage.py check`;
- execução da suíte completa do Django;
- execução de testes Selenium com navegador Chrome real;
- construção reproduzível do ambiente com Docker;
- validação do Docker Compose antes dos testes;
- limpeza automática dos containers e volumes;
- execução automática em Pull Requests;
- uso do resultado dos testes como código de saída da pipeline.

Essas melhorias reduzem o risco de integrar alterações com regressões e
garantem que todos os Pull Requests sejam avaliados em um ambiente reproduzível.

---

## 12. Resultado

A estratégia de testes passou a combinar diferentes níveis de validação:

- testes unitários;
- testes de modelos;
- testes funcionais;
- testes de caracterização;
- testes de aceitação com o cliente Django;
- testes de aceitação com Selenium e Chrome.

A execução local da suíte completa confirmou:

```text
250 testes executados
250 testes aprovados
0 falhas
0 erros
```

A execução do workflow no GitHub Actions deve ser confirmada durante a abertura
do Pull Request que contém as melhorias de Selenium, CI e documentação.