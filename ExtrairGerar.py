import os
import json
import requests
from datetime import datetime


def formatar_data_iso(data_str):
    """Converte a string ISO UTC para o formato brasileiro local."""
    if not data_str:
        return "N/A"
    try:
        data_str = data_str.replace("Z", "")
        dt_utc = datetime.fromisoformat(data_str)
        dt_local = datetime.fromtimestamp(dt_utc.timestamp())
        return dt_local.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return data_str


def chunk_list(lista, n):
    """Divide uma lista em pedaços de tamanho n."""
    for i in range(0, len(lista), n):
        yield lista[i : i + n]


def executar_automacao_freecast():
    # 1. Configurações de Autenticação e Headers
    
TOKEN = os.environ.get("FREECAST_TOKEN", "seu_token_reserva_aqui")


    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    # 2. URLs da API
    url_categorias = "https://api-services.freecast.com/live/api/v10/watch-freecast-com/web/packages/free/categories/"
    url_epg = "https://api-services.freecast.com/live/api/v8/watch-freecast-com/web/packages/free/epgs/"

    print("🛰️  Etapa 1: Varrendo a API para coletar todos os Slugs de canais...")

    try:
        # Busca todas as categorias expandindo os canais
        res_cat = requests.get(
            url_categorias, headers=headers, params={"expand": "channels"}
        )
        res_cat.raise_for_status()
        categorias = res_cat.json()

        # Coleta slugs únicos usando um set
        slugs_unicos = set()
        for cat in categorias:
            for canal in cat.get("channels", []):
                slug = canal.get("slug")
                if slug:
                    slugs_unicos.add(slug)

        lista_slugs = list(slugs_unicos)
        total_canais = len(lista_slugs)
        print(f"✅ Sucesso! Encontrados {total_canais} slugs de canais únicos.\n")

        # 3. Processamento do EPG em lotes de 10 canais
        print(
            f"⏳ Etapa 2: Baixando a programação (EPG) em lotes de 10 canais..."
        )
        epg_completo_json = []

        # Divide os slugs em grupos de 10 (ex: 120 canais = 12 requisições)
        lotes_slugs = list(chunk_list(lista_slugs, 10))

        for idx, lote in enumerate(lotes_slugs, start=1):
            print(
                f" -> Baixando lote {idx}/{len(lotes_slugs)} ({len(lote)} canais)..."
            )

            # Passa o array de 10 slugs nos parâmetros da URL
            params_epg = {"slug": lote}
            try:
                res_epg = requests.get(
                    url_epg, headers=headers, params=params_epg
                )
                res_epg.raise_for_status()
                dados_epg = res_epg.json()

                if isinstance(dados_epg, list):
                    epg_completo_json.extend(dados_epg)

            except requests.exceptions.RequestException as e:
                print(f" ❌ Erro ao baixar o lote {idx}: {e}")
                continue

        # 4. Salvando o arquivo final com o EPG de TODO MUNDO
        arquivo_final = "freecast_epg_completo.json"
        with open(arquivo_final, "w", encoding="utf-8") as f:
            json.dump(epg_completo_json, f, indent=4, ensure_ascii=False)

        print("\n" + "=" * 60)
        print(f"✨ AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📂 Arquivo gerado: '{arquivo_final}'")
        print(
            f"📺 Total de canais com EPG mapeado: {len(epg_completo_json)}"
        )
        print("=" * 60)

        # 5. Print opcional no terminal para checagem rápida do resultado
        print("\n📋 Amostra da programação capturada:")
        for canal in epg_completo_json[:3]:  # Mostra apenas os 3 primeiros
            slug_canal = canal.get("slug", "desconhecido")
            print(f"\n📺 CANAL: {slug_canal.upper()}")
            programas = canal.get("epg_programs", [])

            if programas:
                for prog in programas[:2]:  # Mostra os 2 primeiros programas
                    titulo = prog.get("title", "Sem título")
                    inicio = formatar_data_iso(prog.get("start_time"))
                    print(f"  ⏰ [{inicio}] -> {titulo}")
            else:
                print("  ❌ Sem programas listados para este bloco.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro crítico na comunicação com a API: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    executar_automacao_freecast()
