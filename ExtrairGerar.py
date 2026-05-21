import json
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import os


def formatar_data_xmltv(data_str):
    """Converte a string ISO UTC da API para o formato padrão do XMLTV."""
    if not data_str:
        return ""
    try:
        data_str = data_str.replace("Z", "")
        dt = datetime.fromisoformat(data_str)
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""


def chunk_list(lista, n):
    """Divide uma lista em pedaços de tamanho n."""
    for i in range(0, len(lista), n):
        yield lista[i : i + n]


def gerar_xmltv_freecast():
    # 🌟 CORRIGIDO: Linha agora está com os 4 espaços corretos de indentação!
    # Tenta pegar o token das configurações do GitHub. Se não achar, usa o seu fixo.
    TOKEN = os.environ.get("FREECAST_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwMDkxNjEzLCJqdGkiOiI0MDMyNGFhNDk5OWI0NGZiODUwYTAwNWI1NWIzODA1YyIsInVzZXJfaWQiOjY1MTQwM30.Wruc0S1iEBLBUgHErOUQmBcJMG9XCmY04mtJ3IkDqL4")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    url_categorias = "https://api-services.freecast.com/live/api/v10/watch-freecast-com/web/packages/free/categories/"
    url_epg = "https://api-services.freecast.com/live/api/v8/watch-freecast-com/web/packages/free/epgs/"

    print("🛰️  Etapa 1: Mapeando canais e coletando Slugs...")
    try:
        res_cat = requests.get(url_categorias, headers=headers, params={"expand": "channels"})
        res_cat.raise_for_status()
        categorias = res_cat.json()
    except Exception as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        return

    canais_mapeados = {}
    for cat in categorias:
        for canal in cat.get("channels", []):
            slug = canal.get("slug")
            if slug and slug not in canais_mapeados:
                canais_mapeados[slug] = {
                    "id": canal.get("id") or slug,
                    "nome": canal.get("name") or canal.get("title") or slug.replace("cms-", "").replace("-", " ").title(),
                    "logo": canal.get("logo") or canal.get("thumbnail") or ""
                }

    lista_slugs = list(canais_mapeados.keys())
    print(f"✅ Encontrados {len(lista_slugs)} canais únicos.")

    tv_root = ET.Element("tv")
    tv_root.set("generator-info-name", "FreeCast XMLTV Generator")

    print("📺 Estruturando canais no cabeçalho do XMLTV...")
    for slug, info in canais_mapeados.items():
        channel_elem = ET.SubElement(tv_root, "channel", id=info["id"])
        display_name1 = ET.SubElement(channel_elem, "display-name")
        display_name1.text = info["nome"]
        display_name2 = ET.SubElement(channel_elem, "display-name")
        display_name2.text = slug
        if info["logo"]:
            ET.SubElement(channel_elem, "icon", src=info["logo"])

    print("⏳ Etapa 2: Puxando guias de programação em blocos...")
    lotes_slugs = list(chunk_list(lista_slugs, 10))

    for idx, lote in enumerate(lotes_slugs, start=1):
        print(f" -> Buscando guia do lote {idx}/{len(lotes_slugs)} ({len(lote)} canais)...")
        try:
            res_epg = requests.get(url_epg, headers=headers, params={"slug": lote})
            res_epg.raise_for_status()
            dados_epg = res_epg.json()
            
            for bloco_canal in dados_epg:
                slug_canal = bloco_canal.get("slug")
                if not slug_canal or slug_canal not in canais_mapeados:
                    continue
                
                channel_id = canais_mapeados[slug_canal]["id"]
                programas = bloco_canal.get("epg_programs", [])
                
                for prog in programas:
                    start_time = formatar_data_xmltv(prog.get("start_time"))
                    end_time = formatar_data_xmltv(prog.get("end_time"))
                    titulo_txt = prog.get("title", "Sem título")
                    desc_txt = prog.get("description", "")

                    if not start_time or not end_time:
                        continue

                    prog_elem = ET.SubElement(tv_root, "programme", start=start_time, stop=end_time, channel=channel_id)
                    title_elem = ET.SubElement(prog_elem, "title", lang="en")
                    title_elem.text = titulo_txt
                    if desc_txt:
                        desc_elem = ET.SubElement(prog_elem, "desc", lang="en")
                        desc_elem.text = desc_txt

        except Exception as e:
            print(f" ❌ Falha temporária no bloco {idx}: {e}")
            continue

    print("\n💾 Gravando arquivo XMLTV final...")
    xml_string = ET.tostring(tv_root, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8")

    arquivo_saida = "freecast_epg.xml"
    with open(arquivo_saida, "wb") as f:
        f.write(pretty_xml)
        
    print("=" * 60)
    print(f"✨ SUCESSO! O guia XMLTV foi gerado.")
    print("=" * 60)


if __name__ == '__main__':
    gerar_xmltv_freecast()
