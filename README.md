# 🛰️ FreeCast XMLTV EPG Generator

Este projeto automatiza a extração da grade de programação (EPG) dos canais da plataforma FreeCast e converte os dados para o formato padrão **XMLTV** (`.xml`). O guia gerado é ideal para integração com players de IPTV (como Tivimate, OTT Navigator, Perfect Player) e servidores de mídia (Plex, Jellyfin).

A atualização do guia é 100% automatizada utilizando **GitHub Actions**, rodando todos os dias de forma totalmente independente.

---

## 🚀 Como Funciona a Automação

O fluxo de trabalho configurado no GitHub Actions executa os seguintes passos:
1. Inicializa um ambiente virtual Linux (Ubuntu).
2. Faz o mapeamento completo dos canais da FreeCast descobrindo todos os *slugs*, nomes e logotipos dinamicamente.
3. Divide as requisições em lotes automáticos para coletar a programação completa sem estourar os limites da API.
4. Gera e estrutura o arquivo final `freecast_epg.xml` no formato XMLTV.
5. Faz o commit e atualiza o arquivo automaticamente no repositório.

---

## 📅 Agendamento

* **Automático:** O robô roda todos os dias às **00:00 (Horário de Brasília)** / `03:00 UTC`.
* **Manual:** Pode ser acionado a qualquer momento acessando a aba **Actions** -> **Atualizar EPG FreeCast** -> **Run workflow**.

---

## 🛠️ Como Usar o Link do EPG no seu Player

Após a primeira execução bem-sucedida, o seu arquivo XML estará disponível publicamente. Você pode copiar o link direto (Raw) do GitHub para colar no seu aplicativo de IPTV:

```text
[https://raw.githubusercontent.com/JulioCesarXY/EPG-FreeCast/main/freecast_epg.xml](https://raw.githubusercontent.com/JulioCesarXY/EPG-FreeCast/main/freecast_epg.xml)

