# Validation record / Registro de validação

Review date / Data da revisão: 2026-09-10.

## Change and reason / Mudança e motivo

EN: Restored the missing landing template; validated dates, quantities, references and statuses; serialized in-process access and fixed orphaned guests after deletion.

PT: Restaurado o template ausente; validados datas, quantidades, referências e status; serializado acesso no processo e corrigidos convidados órfãos após exclusão.

## Reproduce / Reproduzir

```sh
python -m venv .venv
# Activate .venv for your shell / Ative .venv no seu terminal
python -m pip install -r requirements-validation.txt
python -m pytest -q
python -m examples.review_demo
```

## Example evidence / Evidência do exemplo

The walkthrough creates event 3, adds a task and guest, and verifies 3 events, 3 guests and a total budget of 76500. / O roteiro cria o evento 3, adiciona tarefa e convidado e verifica 3 eventos, 3 convidados e orçamento total de 76500.

EN: The suite includes normal operations and regression cases for the corrected behavior. The example checks values produced by the implementation. Use the linked workflow to inspect the result for a specific commit; no performance benchmark is inferred from a passing build.

PT: A suíte inclui operações válidas e regressões dos comportamentos corrigidos. O exemplo verifica valores produzidos pela implementação. Consulte a automação para conferir o resultado de um commit específico; aprovação de compilação não implica benchmark de desempenho.

## Limits / Limites

EN: This is a local, single-process prototype with in-memory storage. Restarting clears changes. It has no authentication, persistent database, payments or invitation delivery. Task and event examples are synthetic.

PT: Protótipo local de processo único com armazenamento em memória. Reiniciar apaga alterações. Não possui autenticação, banco persistente, pagamentos ou envio de convites. Os exemplos de tarefas e eventos são fictícios.

[Return to README / Voltar ao README](../README.md)

## Verified suite / Suíte verificada

**32 software tests passed / testes de software aprovados.**

README Mermaid syntax and local documentation links were checked. / A sintaxe Mermaid do README e os links locais da documentação foram conferidos.
