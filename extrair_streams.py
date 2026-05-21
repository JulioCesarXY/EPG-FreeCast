import json
import requests
import os

def extrair_streams_por_categoria():
    TOKEN = os.environ.get("FREECAST_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwMDkxNjEzLCJqdGkiOiI0MDMyNGFhNDk5OWI0NGZiODUwYTAwNWI1NWIzODA1YyIsInVzZXJfaWQiOjY1MTQwM30.Wruc0S1iEBLBUgHErOUQmBcJMG9XCmY04mtJ3IkDqL4")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    url_categorias = "https://api-services.freecast.com/live/api/v10/watch-freecast-com/web/packages/free/categories/"
    
    print("🛰️  Coletando categorias e canais da FreeCast...")
    try:
        res_cat = requests.get(url_categorias, headers=headers, params={"expand": "channels"})
        res_cat.raise_for_status()
        categorias = res_cat.json()
    except Exception as e:
        print(f"❌ Erro ao buscar dados de origem: {e}")
        return

    # Passo 1: Mapear a qual categoria cada canal pertence
    # Um canal pode estar em mais de uma categoria, mas para o M3U vamos definir a primeira que ele aparecer
    print("📂 Mapeando estrutura de grupos...")
    canais_com_categoria = {}
    
    for cat in categorias:
        nome_categoria = cat.get("name", "Geral").strip()
        
        # Ignora categorias vazias ou muito genéricas se preferir (ex: "All")
        if nome_categoria.lower() == "all":
            continue
            
        for canal in cat.get("channels", []):
            slug = canal.get("slug")
            if slug and slug not in canais_com_categoria:
                canais_com_categoria[slug] = {
                    "id": canal.get("id") or slug,
                    "nome": canal.get("name") or canal.get("title") or slug.replace("cms-", "").replace("-", " ").title(),
                    "logo": canal.get("logo") or canal.get("thumbnail") or "",
                    "categoria": nome_categoria # Atribui o grupo/categoria
                }

    print(f"✅ Mapeamento concluído! {len(canais_com_categoria)} canais prontos para checagem de stream.\n")
    print("⏳ Iniciando extração dos links m3u8...")
    print("=" * 60)

    lista_m3u_linhas = ["#EXTM3U\n"]
    canais_com_sucesso = 0

    # Passo 2: Buscar o link de stream de cada canal mapeado
    for idx, (slug, info) in enumerate(canais_com_categoria.items(), start=1):
        url_streams = f"https://api-services.freecast.com/live/api/v8/watch-freecast-com/web/packages/free/channels/{slug}/streams/"
        
        print(f"[{idx}/{len(canais_com_categoria)}] [{info['categoria']}] Puxando: {info['nome']}...")
        
        try:
            res_stream = requests.get(url_streams, headers=headers)
            
            if res_stream.status_code == 404:
                url_streams_alt = url_streams.replace("api/v8", "api/v10")
                res_stream = requests.get(url_streams_alt, headers=headers)

            if res_stream.status_code == 200:
                dados_stream = res_stream.json()
                stream_url = ""
                
                # Validação baseada no print do json de debug anterior
                if "streams" in dados_stream and isinstance(dados_stream["streams"], list) and len(dados_stream["streams"]) > 0:
                    stream_url = dados_stream["streams"][0].get("data")

                if stream_url:
                    print(f"  🔗 [OK]: {stream_url[:65]}...")
                    
                    # 🌟 INJEÇÃO DO GROUP-TITLE: Define a categoria separada para o Player organizar em abas
                    linha_m3u = f'#EXTINF:-1 tvg-id="{info["id"]}" tvg-name="{slug}" tvg-logo="{info["logo"]}" group-title="{info["categoria"]}", {info["nome"]}\n{stream_url}\n'
                    lista_m3u_linhas.append(linha_m3u)
                    canais_com_sucesso += 1
                else:
                    print("  ⚠️  Link de transmissão não encontrado dentro de 'streams'.")
            else:
                print(f"  ❌ Erro HTTP {res_stream.status_code}")

        except Exception as e:
            print(f"  ❌ Falha na requisição do canal: {e}")
        
        print("-" * 50)

    # Passo 3: Salvar o arquivo final
    if canais_com_sucesso > 0:
        arquivo_m3u = "freecast_canais.m3u"
        with open(arquivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lista_m3u_linhas)
        print("\n" + "=" * 60)
        print(f"✨ PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📂 Arquivo M3U categorizado gerado com {canais_com_sucesso} canais ativos.")
        print(f"💾 Nome do arquivo: '{arquivo_m3u}'")
        print("=" * 60)
    else:
        print("\n❌ Nenhum link pôde ser extraído.")

if __name__ == "__main__":
    extrair_streams_por_categoria()
