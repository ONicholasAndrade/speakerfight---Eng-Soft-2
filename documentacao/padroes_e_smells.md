# Padrões de Projeto e Code Smells

## 1. Objetivo

Este documento registra a identificação, a refatoração e a validação de três *code smells* encontrados no projeto Speakerfight.

Para cada ocorrência são apresentados:

- localização no código;
- trecho anterior à refatoração;
- problema identificado;
- técnica aplicada;
- trecho posterior à refatoração;
- princípios e padrões relacionados;
- testes utilizados;
- resultado da análise de qualidade.

As refatorações foram implementadas no PR #7 e validadas por testes automatizados e pela análise estática realizada com o Radon 4.3.2.

---

## 2. Resumo das ocorrências

| Nº | Code smell | Localização | Solução aplicada |
|---:|---|---|---|
| 1 | Long Method | `ListEvents.get_queryset()` em `deck/views.py` | Extract Method |
| 2 | Switch Statement | `Proposal.user_can_vote()` em `deck/models.py` | Cadeia de regras inspirada em Chain of Responsibility |
| 3 | Long Method e código duplicado | `RateProposal.dispatch()`, `ApproveProposal.dispatch()` e `DisapproveProposal.dispatch()` em `deck/views.py` | Template Method por meio de `ProposalActionView` |

Não foi identificado um caso tecnicamente defensável de **Long Parameter List** nos arquivos analisados. Por esse motivo, foram selecionadas duas ocorrências relacionadas a Long Method e uma ocorrência de Switch Statement.

---

## 3. Critérios utilizados

### 3.1 Long Method

Um método pode apresentar Long Method quando concentra muitas linhas, decisões e responsabilidades diferentes.

Foram considerados os seguintes sinais:

- `NLOC`: quantidade de linhas sem comentários;
- `CYCLO`: complexidade ciclomática;
- `NOAV`: quantidade de variáveis e objetos acessados;
- `MAXNESTING`: nível de aninhamento;
- quantidade de responsabilidades reunidas no mesmo método;
- dificuldade de testar partes do fluxo isoladamente.

### 3.2 Switch Statement

O smell Switch Statement não exige a existência de uma instrução `switch` literal.

Em Python, ele também pode aparecer como uma cadeia rígida de `if/elif/else` que escolhe o comportamento a partir de estados, papéis ou categorias.

Os sinais considerados foram:

- existência de vários casos;
- dependência da ordem das condições;
- necessidade de alterar o mesmo método para adicionar uma nova regra;
- ausência de delegação para regras ou objetos especializados.

### 3.3 Código duplicado

Código duplicado ocorre quando diferentes partes do sistema repetem a mesma estrutura ou comportamento.

Os principais riscos são:

- uma correção ser aplicada somente em uma das cópias;
- comportamentos semelhantes se tornarem inconsistentes;
- aumento do esforço de manutenção;
- dificuldade para criar novas ações que reutilizem o mesmo fluxo.

---

# 4. Smell 1 — Long Method em `ListEvents.get_queryset()`

## 4.1 Localização

```text
Arquivo: deck/views.py
Classe: ListEvents
Método: get_queryset
```

## 4.2 Código anterior

```python
def get_queryset(self):
    queryset = super(ListEvents, self).get_queryset()
    queryset = queryset.published_ones()

    # When it should only show past events
    if self.past_events:
        queryset = queryset.filter(closing_date__lt=timezone.now())

    criteria = self.request.GET.get(u'search', None)
    if criteria:
        queryset = queryset.filter(
            models.Q(title__icontains=criteria) |
            models.Q(description__icontains=criteria)
        )
    elif not self.past_events:
        queryset = queryset.upcoming()

    paginator = Paginator(queryset, 15)
    page = self.request.GET.get('page')

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    return queryset
```

## 4.3 Problema identificado

O método reunia responsabilidades diferentes:

1. obter o queryset;
2. selecionar eventos publicados;
3. filtrar eventos passados;
4. filtrar eventos futuros;
5. pesquisar por título e descrição;
6. criar o paginador;
7. tratar página não numérica;
8. tratar página acima do limite.

Qualquer mudança relacionada a pesquisa, período ou paginação exigia alterar o mesmo método.

O fluxo também dificultava testes isolados, porque filtragem e paginação estavam concentradas no mesmo bloco.

Na análise do Radon, o método apresentava complexidade:

```text
B (6)
```

## 4.4 Técnica aplicada

Foi aplicada a técnica **Extract Method**.

As etapas foram separadas em métodos com nomes explícitos:

- `apply_filters()`;
- `filter_past_events()`;
- `get_search_criteria()`;
- `filter_by_search()`;
- `paginate_events()`.

Também foi criado o atributo:

```python
events_per_page = 15
```

Assim, o valor usado na paginação deixou de ficar fixo dentro do método.

## 4.5 Código posterior

```python
class ListEvents(BaseEventView, ListView):
    allow_empty = True
    past_events = False
    events_per_page = 15

    def get_queryset(self):
        queryset = super(ListEvents, self).get_queryset()
        queryset = queryset.published_ones()
        queryset = self.apply_filters(queryset)

        return self.paginate_events(queryset)

    def apply_filters(self, queryset):
        if self.past_events:
            queryset = self.filter_past_events(queryset)

        criteria = self.get_search_criteria()

        # Search is applied to the queryset after the past-events filter.
        # In the regular list, searching preserves the original behavior and
        # does not restrict the result to upcoming events.
        if criteria:
            return self.filter_by_search(queryset, criteria)

        if not self.past_events:
            return queryset.upcoming()

        return queryset

    def filter_past_events(self, queryset):
        return queryset.filter(
            closing_date__lt=timezone.now()
        )

    def get_search_criteria(self):
        return self.request.GET.get(u'search', None)

    def filter_by_search(self, queryset, criteria):
        return queryset.filter(
            models.Q(title__icontains=criteria) |
            models.Q(description__icontains=criteria)
        )

    def paginate_events(self, queryset):
        paginator = Paginator(queryset, self.events_per_page)
        page = self.request.GET.get('page')

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
```

## 4.6 Princípios e boas práticas relacionados

### Single Responsibility Principle — SRP

Cada método passou a cuidar de uma etapa específica:

- `get_queryset()` coordena o fluxo;
- `apply_filters()` organiza a aplicação dos filtros;
- `filter_by_search()` executa a pesquisa;
- `paginate_events()` trata a paginação.

### Separação de responsabilidades

A construção da consulta deixou de ficar misturada com o tratamento de páginas inválidas.

### Legibilidade

Os nomes dos métodos permitem compreender o fluxo sem analisar todos os detalhes internos de uma só vez.

> Extract Method é uma técnica de refatoração, e não um padrão de projeto GoF.

## 4.7 Testes utilizados

Foram utilizados testes de caracterização em:

```text
deck/tests/test_refactoring.py
```

Cenários protegidos:

- pesquisa por descrição;
- pesquisa comum preservando o comportamento existente com evento passado;
- página não numérica retornando a primeira página;
- página acima do limite retornando a última página;
- listagem de eventos passados;
- pesquisa em `past_events=True` considerando somente eventos passados.

Também foram executados os testes funcionais existentes de eventos:

```text
deck.tests.test_functional.EventTest
```

## 4.8 Resultado

A complexidade de `ListEvents.get_queryset()` foi reduzida de:

```text
B (6) → A (1)
```

A classe `ListEvents` passou de:

```text
A (5) → A (2)
```

A lógica foi distribuída em métodos menores sem alterar o comportamento protegido pelos testes.

---

# 5. Smell 2 — Switch Statement em `Proposal.user_can_vote()`

## 5.1 Localização

```text
Arquivo: deck/models.py
Classe: Proposal
Método: user_can_vote
```

## 5.2 Código anterior

```python
def user_can_vote(self, user):
    can_vote = False

    if self.author == user and not self.event.author == user:
        pass
    elif self.event.allow_public_voting:
        can_vote = True
    elif user.is_superuser:
        can_vote = True
    elif self.event.jury.users.filter(pk=user.pk).exists():
        can_vote = True

    return can_vote
```

## 5.3 Problema identificado

O método utilizava uma cadeia rígida de condições para decidir se o usuário poderia votar.

A ordem era importante:

1. autor da proposta;
2. votação pública;
3. superusuário;
4. integrante do júri;
5. negação por padrão.

A inclusão de uma nova regra exigiria editar a cadeia central de `if/elif`.

O uso de `pass` no primeiro caso também reduzia a clareza, pois era necessário chegar ao final do método para concluir que o resultado seria `False`.

Na análise do Radon, o método apresentava complexidade:

```text
B (6)
```

## 5.4 Técnica aplicada

A decisão foi dividida em regras independentes:

- `_deny_proposal_author_vote()`;
- `_allow_public_vote()`;
- `_allow_superuser_vote()`;
- `_allow_jury_vote()`.

O método `get_voting_rules()` fornece a sequência das regras.

Cada regra pode retornar:

- `True`: voto permitido;
- `False`: voto negado;
- `None`: a próxima regra deve ser consultada.

## 5.5 Código posterior

```python
def user_can_vote(self, user):
    for rule in self.get_voting_rules():
        decision = rule(user)

        if decision is not None:
            return decision

    return False

def get_voting_rules(self):
    return (
        self._deny_proposal_author_vote,
        self._allow_public_vote,
        self._allow_superuser_vote,
        self._allow_jury_vote,
    )

def _deny_proposal_author_vote(self, user):
    if self.author == user and self.event.author != user:
        return False

    return None

def _allow_public_vote(self, user):
    if self.event.allow_public_voting:
        return True

    return None

def _allow_superuser_vote(self, user):
    if user.is_superuser:
        return True

    return None

def _allow_jury_vote(self, user):
    if self.event.jury.users.filter(pk=user.pk).exists():
        return True

    return None
```

## 5.6 Padrão e princípios relacionados

### Cadeia de regras inspirada em Chain of Responsibility

A implementação segue a ideia central do padrão:

1. existe uma sequência ordenada de regras;
2. cada regra recebe a oportunidade de decidir;
3. uma regra pode devolver uma resposta;
4. quando não decide, o processamento continua na próxima regra.

A implementação não utiliza classes de *handlers* encadeadas por referências, como na forma clássica do padrão. Por isso, a descrição tecnicamente mais precisa é:

> cadeia de regras inspirada em Chain of Responsibility.

### Open/Closed Principle — OCP

Uma nova regra pode ser criada como outro método e incluída na sequência retornada por `get_voting_rules()`.

### Single Responsibility Principle — SRP

Cada método representa uma regra de autorização específica.

### Legibilidade

Os nomes dos métodos documentam o motivo de permitir ou negar o voto.

## 5.7 Testes utilizados

Foram utilizados os testes existentes de `Proposal.user_can_vote()` e os testes funcionais de propostas.

Cenários preservados:

- autor da proposta não pode votar na própria proposta quando não é o autor do evento;
- votação pública permite o voto;
- superusuário pode votar;
- integrante do júri pode votar;
- usuário sem permissão recebe `False`;
- a ordem das regras continua preservada.

Comandos utilizados na validação:

```bash
python manage.py test deck.tests.test_models
python manage.py test deck.tests.test_functional.ProposalTest
```

## 5.8 Resultado

A complexidade de `Proposal.user_can_vote()` foi reduzida de:

```text
B (6) → A (3)
```

A classe `Proposal` passou de:

```text
A (4) → A (3)
```

As regras ficaram explícitas e separadas, mantendo a ordem de decisão original.

---

# 6. Smell 3 — Long Method e duplicação nas ações de propostas

## 6.1 Localização

```text
Arquivo: deck/views.py
Classes:
- RateProposal
- ApproveProposal
- DisapproveProposal

Métodos:
- RateProposal.dispatch()
- ApproveProposal.dispatch()
- DisapproveProposal.dispatch()
```

## 6.2 Código anterior

A estrutura abaixo existia em `RateProposal.dispatch()`:

```python
def dispatch(self, *args, **kwargs):
    proposal = self.get_object()
    view_event_url = reverse(
        'view_event',
        kwargs={'slug': proposal.event.slug}
    )

    if not self.request.user.is_authenticated():
        message = _(
            u'You need to be logged in to '
            u'continue to the next step.'
        )

        if self.request.method == 'GET':
            messages.error(self.request, message)
            return HttpResponseRedirect(view_event_url)

        response = {}
        response['message'] = message
        response['redirectUrl'] = u'{}?{}={}'.format(
            settings.LOGIN_URL,
            REDIRECT_FIELD_NAME,
            self.request.META.get('PATH_INFO')
        )

        return HttpResponse(
            json.dumps(response),
            status=401,
            content_type='application/json'
        )

    elif not proposal.user_can_vote(self.request.user):
        message = _(u'You are not allowed to see this page.')

        if self.request.method == 'GET':
            messages.error(self.request, message)
            return HttpResponseRedirect(view_event_url)

        response = {}
        response['message'] = message
        response['redirectUrl'] = ''

        return HttpResponse(
            json.dumps(response),
            status=401,
            content_type='application/json'
        )

    return super(RateProposal, self).dispatch(*args, **kwargs)
```

`ApproveProposal.dispatch()` e `DisapproveProposal.dispatch()` repetiam o mesmo fluxo. A principal diferença era a regra específica de autorização:

```python
proposal.user_can_vote(self.request.user)
```

ou:

```python
proposal.user_can_approve(self.request.user)
```

## 6.3 Problema identificado

Cada método reunia:

- recuperação da proposta;
- autenticação;
- autorização;
- criação de mensagem;
- construção da URL de login;
- diferenciação entre GET e POST;
- redirecionamento HTML;
- resposta JSON;
- status HTTP 401;
- continuação do fluxo da View.

Além do tamanho, havia duplicação entre três classes.

Uma mudança na estrutura de resposta ou na mensagem de erro teria de ser repetida em todos os métodos.

Antes da refatoração, o Radon apresentou:

```text
RateProposal.dispatch()       A (5)
ApproveProposal.dispatch()    A (5)
DisapproveProposal.dispatch() A (5)
```

## 6.4 Técnica e padrão aplicados

Foi criada a classe-base:

```text
ProposalActionView
```

Ela define o fluxo comum de autenticação e autorização.

O método:

```python
user_has_permission()
```

representa a etapa variável e deve ser implementado pelas subclasses.

Essa estrutura aplica o padrão **Template Method**:

- a classe-base define o esqueleto do algoritmo;
- as subclasses especializam apenas uma etapa;
- o fluxo geral permanece centralizado.

Também foram extraídos métodos auxiliares:

- `get_view_event_url()`;
- `get_login_redirect_url()`;
- `get_denied_response()`.

## 6.5 Código posterior

### Classe-base

```python
class ProposalActionView(BaseProposalView, UpdateView):

    def user_has_permission(self, proposal):
        raise NotImplementedError

    def get_view_event_url(self, proposal):
        return reverse(
            'view_event',
            kwargs={'slug': proposal.event.slug}
        )

    def get_login_redirect_url(self):
        return u'{}?{}={}'.format(
            settings.LOGIN_URL,
            REDIRECT_FIELD_NAME,
            self.request.META.get('PATH_INFO')
        )

    def get_denied_response(self, proposal, message, redirect_url):
        if self.request.method == 'GET':
            messages.error(self.request, message)
            return HttpResponseRedirect(
                self.get_view_event_url(proposal)
            )

        response = {
            'message': message,
            'redirectUrl': redirect_url,
        }

        return HttpResponse(
            json.dumps(response),
            status=401,
            content_type='application/json'
        )

    def dispatch(self, *args, **kwargs):
        proposal = self.get_object()

        if not self.request.user.is_authenticated():
            message = _(
                u'You need to be logged in to '
                u'continue to the next step.'
            )

            return self.get_denied_response(
                proposal,
                message,
                self.get_login_redirect_url()
            )

        if not self.user_has_permission(proposal):
            message = _(u'You are not allowed to see this page.')

            return self.get_denied_response(
                proposal,
                message,
                u''
            )

        return super(ProposalActionView, self).dispatch(
            *args,
            **kwargs
        )
```

### Especializações

```python
class RateProposal(ProposalActionView):

    def user_has_permission(self, proposal):
        return proposal.user_can_vote(self.request.user)
```

```python
class ApproveProposal(ProposalActionView):

    def user_has_permission(self, proposal):
        return proposal.user_can_approve(self.request.user)
```

```python
class DisapproveProposal(ProposalActionView):

    def user_has_permission(self, proposal):
        return proposal.user_can_approve(self.request.user)
```

## 6.6 Padrões e princípios relacionados

### Template Method

`ProposalActionView.dispatch()` define o fluxo fixo:

1. recuperar a proposta;
2. verificar autenticação;
3. consultar a autorização;
4. gerar a resposta de negação quando necessário;
5. continuar o processamento da View.

As subclasses implementam somente a etapa variável:

```python
user_has_permission()
```

### Don't Repeat Yourself — DRY

O fluxo duplicado foi centralizado em uma única classe.

### Single Responsibility Principle — SRP

Os métodos auxiliares separam:

- construção da URL do evento;
- construção da URL de login;
- montagem da resposta de acesso negado;
- decisão de permissão.

### Open/Closed Principle — OCP

Uma nova ação sobre propostas pode herdar de `ProposalActionView` e implementar sua regra de permissão sem copiar o fluxo completo.

## 6.7 Testes utilizados

Foram utilizados:

```text
deck.tests.test_functional.ProposalTest
deck.tests.test_models
```

Os testes verificam comportamentos como:

- usuário não autenticado;
- usuário sem permissão;
- usuário autorizado;
- resposta de redirecionamento para GET;
- resposta JSON para POST;
- votação;
- aprovação;
- desaprovação.

Também foi executada a suíte completa para verificar possíveis efeitos em outros módulos.

## 6.8 Resultado

Os três métodos duplicados deixaram de existir.

Eles foram substituídos por:

```text
ProposalActionView.dispatch() A (3)
```

As regras específicas ficaram com complexidade:

```text
RateProposal.user_has_permission()       A (1)
ApproveProposal.user_has_permission()    A (1)
DisapproveProposal.user_has_permission() A (1)
```

A duplicação foi eliminada e o fluxo comum ficou centralizado.

---

# 7. Testes de caracterização e regressão

## 7.1 Objetivo

Os testes foram utilizados para registrar o comportamento existente antes das refatorações e verificar que as mudanças internas não alteraram as regras do sistema.

## 7.2 Arquivo criado

```text
deck/tests/test_refactoring.py
```

## 7.3 Cenários adicionados

Os cenários relacionados à listagem de eventos incluem:

1. pesquisa por descrição;
2. pesquisa comum podendo retornar evento passado, conforme o comportamento original;
3. página não numérica retornando a primeira página;
4. página acima do limite retornando a última página;
5. rota de eventos passados retornando o evento esperado;
6. pesquisa na rota de eventos passados considerando somente eventos passados.

## 7.4 Suítes utilizadas

```bash
python manage.py test deck.tests.test_refactoring
python manage.py test deck.tests.test_functional.EventTest
python manage.py test deck.tests.test_functional.ProposalTest
python manage.py test deck.tests.test_models
python manage.py test
```

Todos os testes executados após as refatorações foram aprovados.

---

# 8. Resultado da análise de qualidade

A análise foi realizada com o Radon 4.3.2.

## 8.1 Complexidade dos pontos refatorados

| Elemento | Antes | Depois |
|---|---:|---:|
| `ListEvents.get_queryset()` | B (6) | A (1) |
| `Proposal.user_can_vote()` | B (6) | A (3) |
| `RateProposal.dispatch()` | A (5) | Removido |
| `ApproveProposal.dispatch()` | A (5) | Removido |
| `DisapproveProposal.dispatch()` | A (5) | Removido |
| `ProposalActionView.dispatch()` | Inexistente | A (3) |

## 8.2 Resultado geral

| Métrica | Antes | Depois |
|---|---:|---:|
| Complexidade média | A (2,34) | A (2,03) |
| Manutenibilidade de `views.py` | B (18,88) | A (20,59) |
| Manutenibilidade de `models.py` | A (24,43) | A (22,82) |
| Linhas lógicas totais | 667 | 652 |

O arquivo `models.py` apresentou uma pequena redução numérica no índice de manutenibilidade, mas permaneceu na classificação A. Ao mesmo tempo, a complexidade concentrada de `user_can_vote()` foi reduzida.

O relatório completo está disponível em:

```text
documentacao/analise_qualidade.md
```

As evidências estão em:

```text
documentacao/evidencias/qualidade/
```

---

# 9. Princípios e padrões consolidados

| Aplicação | Classificação | Justificativa |
|---|---|---|
| Extract Method em `ListEvents` | Técnica de refatoração | Divide filtragem e paginação em métodos menores |
| Cadeia de regras em `Proposal.user_can_vote()` | Estrutura inspirada em Chain of Responsibility | Cada regra pode decidir ou transferir a decisão para a próxima |
| `ProposalActionView` | Template Method | A classe-base define o fluxo e as subclasses fornecem a etapa variável |
| SRP | Princípio | Métodos e regras passaram a ter responsabilidades mais específicas |
| OCP | Princípio | Novas regras e ações podem ser adicionadas com menor repetição |
| DRY | Boa prática | Remove a duplicação dos métodos `dispatch()` |

É importante diferenciar:

- **padrão de projeto aplicado diretamente:** Template Method;
- **estrutura inspirada em padrão:** cadeia de regras inspirada em Chain of Responsibility;
- **técnica de refatoração:** Extract Method;
- **princípios e boas práticas:** SRP, OCP e DRY.

---

# 10. Evidências de implementação

## 10.1 Commits

```text
424bbef — refactor(eventos): separa responsabilidades da listagem
32d2d5d — refactor(propostas): organiza regras de permissão para votação
c2725d6 — refactor: conclui refatorações de eventos e propostas
```

## 10.2 Pull Request

```text
PR #7 — refactor: remove code smells em eventos e propostas
```

O PR foi revisado e aprovado antes da integração.

---

# 11. Conclusão

Os três code smells selecionados foram confirmados, refatorados e validados.

A refatoração de `ListEvents.get_queryset()` separou as responsabilidades de filtragem, pesquisa e paginação.

A refatoração de `Proposal.user_can_vote()` transformou uma cadeia centralizada de condições em regras independentes e ordenadas.

A criação de `ProposalActionView` removeu a duplicação existente nas ações de votar, aprovar e desaprovar propostas, aplicando Template Method.

Os resultados do Radon indicaram redução da complexidade dos métodos escolhidos e melhoria da manutenibilidade de `views.py`.

A suíte automatizada permaneceu aprovada, indicando que as mudanças estruturais preservaram o comportamento funcional do sistema.
