"""Gera o feed RSS do podcast "Horóscopo do Dia com a Dina" (só biblioteca padrão do Python).

Só entram os episódios cuja data já chegou em Brasília, então os áudios podem ser enviados com antecedência.
Uso: python3 podcast/gerar_feed.py [pasta]   (lê pasta/podcast.json e pasta/episodios.json; padrão: podcast/)
Serve para mais de um podcast: o campo "guid" do podcast.json prefixa o id dos episódios e "hora" é a hora de saída.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.utils import format_datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")
IT = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ET.register_namespace("itunes", IT)


def _sub(pai, tag, texto=None, **attrs):
    el = ET.SubElement(pai, tag, {k: str(v) for k, v in attrs.items()})
    if texto is not None:
        el.text = str(texto)
    return el


def gerar_feed(pod: dict, episodios: list, hoje: date) -> str:
    rss = ET.Element("rss", {"version": "2.0"})
    c = _sub(rss, "channel")
    _sub(c, "title", pod["titulo"])
    _sub(c, "link", pod["site"])
    _sub(c, "description", pod["descricao"])
    _sub(c, "language", pod["idioma"])
    _sub(c, f"{{{IT}}}author", pod["autor"])
    _sub(c, f"{{{IT}}}summary", pod["descricao"])
    _sub(c, f"{{{IT}}}explicit", "false")
    _sub(c, f"{{{IT}}}type", "episodic")
    _sub(c, f"{{{IT}}}image", href=pod["base"] + pod["capa"])
    cat = _sub(c, f"{{{IT}}}category", text=pod["categoria"])
    if pod.get("subcategoria"):
        _sub(cat, f"{{{IT}}}category", text=pod["subcategoria"])
    dono = _sub(c, f"{{{IT}}}owner")
    _sub(dono, f"{{{IT}}}name", pod["autor"])
    if pod.get("email"):
        _sub(dono, f"{{{IT}}}email", pod["email"])
    for ep in sorted((e for e in episodios if date.fromisoformat(e["data"]) <= hoje), key=lambda e: e["data"], reverse=True):
        d = date.fromisoformat(ep["data"])
        i = _sub(c, "item")
        _sub(i, "title", ep["titulo"])
        _sub(i, "description", ep["descricao"])
        _sub(i, f"{{{IT}}}summary", ep["descricao"])
        _sub(i, "enclosure", url=pod["base"] + ep["arquivo"], length=ep["bytes"], type="audio/mpeg")
        _sub(i, "guid", f"{pod.get('guid', 'dinohoroscopo')}-{ep['data']}", isPermaLink="false")
        _sub(i, "pubDate", format_datetime(datetime(d.year, d.month, d.day, pod.get("hora", 4), 0, tzinfo=TZ)))
        _sub(i, f"{{{IT}}}duration", ep["duracao_s"])
        _sub(i, f"{{{IT}}}explicit", "false")
        _sub(i, f"{{{IT}}}episodeType", ep.get("tipo", "full"))
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="unicode")


def main(argv=None):
    """argv[0] (opcional) = pasta do podcast, com podcast.json e episodios.json; o feed.xml é gravado nela."""
    argv = sys.argv[1:] if argv is None else argv
    pasta = argv[0] if argv else os.path.dirname(os.path.abspath(__file__))
    pod = json.load(open(os.path.join(pasta, "podcast.json"), encoding="utf-8"))
    eps = json.load(open(os.path.join(pasta, "episodios.json"), encoding="utf-8"))
    hoje = datetime.now(TZ).date()
    with open(os.path.join(pasta, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(gerar_feed(pod, eps, hoje))
    print(f"feed.xml: {sum(1 for e in eps if date.fromisoformat(e['data']) <= hoje)} episódio(s) até {hoje}")


if __name__ == "__main__":
    main()
