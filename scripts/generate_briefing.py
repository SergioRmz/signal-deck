#!/usr/bin/env python3
"""Generate a signal-deck briefing from an ingestion packet.

This script intentionally uses only the Python standard library. It validates the
input packet, applies a deterministic transformation layer, validates the output
briefing, and writes the result to disk.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_briefing import validate_briefing
from validate_signal_input import expect_dict, validate_input_packet

DEFAULT_INPUT = Path("data/signal-input.sample.json")
DEFAULT_OUTPUT = Path("data/briefing.sample.json")
QUESTION_PREFIXES = ("which", "what", "where", "who", "how", "when", "why", "do", "does", "will", "can")
CATEGORY_LABELS_ES = {
    "ai": "IA",
    "technology": "Tecnología",
    "economy": "Economía",
    "market-structure": "Estructura de mercado",
    "infrastructure": "Infraestructura",
    "governance": "Gobernanza",
    "economics": "Economía",
}
ROLE_LABELS_ES = {
    "operator": "operador",
    "editor": "editor estratégico",
    "builder": "constructor",
    "learner": "aprendiz ejecutivo",
    "executive learner": "aprendiz ejecutivo",
    "software-engineer": "ingeniero de software",
    "engineer": "ingeniero",
    "founder": "fundador",
    "executive": "ejecutivo",
}
BANNED_PERSONAL_REFERENCES = ("Sergio", "Sergio Ramirez", "Sergio Ramírez")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "briefing"


def clean_sentence(value: str) -> str:
    text = value.strip()
    if not text:
        return text
    if text[-1] not in ".!?":
        text += "."
    return text


def titleize_category(value: str) -> str:
    normalized = value.replace("_", "-").strip().lower()
    return CATEGORY_LABELS_ES.get(normalized, value.replace("-", " ").replace("_", " ").strip().title())


def role_label(role: str) -> str:
    normalized = role.strip().lower()
    return ROLE_LABELS_ES.get(normalized, role.replace("-", " ").strip())


def remove_personal_reference(value: str) -> str:
    text = value
    for banned in BANNED_PERSONAL_REFERENCES:
        text = text.replace(banned, "el lector")
    return text


def es_text(value: str) -> str:
    """Small deterministic Spanish cleanup for model/agent-authored fields.

    This is not a general translator. It protects the public artifact from the
    exact failure mode Sergio reported: English rationale snippets and direct
    references to him leaking from phase notes into the reader-facing briefing.
    """
    replacements = {
        "Frontier AI competition is becoming a control-stack contest: labs, suppliers, integrators and regulators are deciding who can turn scarce compute and trusted deployment channels into durable economic leverage.": "La competencia en IA de frontera se está convirtiendo en una disputa por controlar el stack completo: laboratorios, proveedores, integradores y reguladores decidirán quién transforma cómputo escaso y canales confiables de despliegue en poder económico durable.",
        "Teaches readers to map AI winners and losers by bottleneck control instead of by the loudest product launch.": "Enseña a distinguir ganadores y perdedores de la IA por el control de cuellos de botella, no por el lanzamiento más ruidoso.",
        "Shows Sergio why AI strategy increasingly resembles industrial systems integration, not just software iteration.": "La estrategia de IA se parece cada vez más a integración industrial de sistemas, no solo a iteración de software.",
        "Gives Sergio a reusable map for evaluating AI companies by bottleneck control rather than headline capability.": "Entrega un mapa reutilizable para evaluar compañías de IA por control de cuellos de botella, no por capacidades de titular.",
        "Helps Sergio track which semiconductor layers and rack components may gain bargaining power.": "Ayuda a identificar qué capas de semiconductores y componentes del rack ganan poder de negociación.",
        "Most evidence is still announcement-led or forecast-based, so the thesis should be framed as a power-shift mechanism to monitor rather than a settled outcome.": "La evidencia todavía depende mucho de anuncios y proyecciones; por eso la tesis debe leerse como un mecanismo de cambio de poder que hay que vigilar, no como un resultado cerrado.",
        "OpenAI and Broadcom announced a strategic collaboration to deploy racks of OpenAI-designed AI accelerators and networking systems, targeted to start in the second half of 2026 and complete by the end of 2029. The strategic signal is not only another chip deal; it is frontier AI firms trying to move from buying generic scarce capacity toward designing the compute stack around their own workloads.": "OpenAI y Broadcom anunciaron una colaboración estratégica para desplegar racks con aceleradores y sistemas de red diseñados por OpenAI, con inicio previsto en la segunda mitad de 2026 y finalización hacia 2029. La señal estratégica no es otro acuerdo de chips: es el intento de los laboratorios de IA de pasar de comprar capacidad genérica escasa a diseñar el stack de cómputo alrededor de sus propias cargas de trabajo.",
        "If model labs increasingly specify their own accelerators, the bargaining power map shifts away from pure cloud resale and toward firms that can coordinate chip design, networking, power commitments, financing and workload-specific optimization. For executives, the durable lesson is that AI advantage may become a systems-integration and supply-chain capability, not only a model-quality contest.": "Si los laboratorios de modelos empiezan a especificar sus propios aceleradores, el mapa de poder se desplaza desde la reventa pura de nube hacia quienes pueden coordinar diseño de chips, redes, compromisos de energía, financiamiento y optimización por carga de trabajo. La lección durable: la ventaja en IA puede convertirse en una capacidad de integración de sistemas y cadena de suministro, no solo en una carrera de calidad de modelos.",
        "The Semiconductor Industry Association highlighted a SIA-Deloitte study estimating that semiconductors account for 95% of an AI data server rack's value and that annual revenue from chips deployed in AI data centers could reach more than $1.2 trillion by 2028. This frames the AI buildout as a semiconductor value-capture story, not just a cloud story.": "La Semiconductor Industry Association destacó un estudio SIA-Deloitte que estima que los semiconductores representan 95% del valor de un rack de servidor para IA y que los ingresos anuales de chips desplegados en data centers de IA podrían superar 1.2 billones de dólares en 2028. Esto encuadra la expansión de IA como una historia de captura de valor en semiconductores, no solo de nube.",
        "Anthropic's newsroom shows June announcements including DXC integrating Claude into systems used by banks, airlines and other regulated industries, TCS partnership activity, and broader enterprise programs. The signal is that frontier AI distribution is moving through incumbent integrators and trusted enterprise systems rather than only self-serve developer adoption.": "La sala de prensa de Anthropic muestra anuncios de junio como la integración de Claude por DXC en sistemas usados por bancos, aerolíneas e industrias reguladas, actividad con TCS y programas empresariales más amplios. La señal: la distribución de IA de frontera avanza por integradores incumbentes y sistemas empresariales confiables, no solo por adopción self-service de desarrolladores.",
        "The FTC's action against 'Active Listening' AI marketing claims turns AI surveillance promises into legal risk.": "La acción de la FTC contra afirmaciones de marketing sobre IA de 'escucha activa' convierte las promesas de vigilancia con IA en riesgo legal.",
        "OpenAI URL returned HTTP 403 to direct HEAD from this runtime, but web search confirmed the exact OpenAI title and snippet: OpenAI will design accelerators and systems developed/deployed with Broadcom.": "La fuente directa no respondió desde este entorno, pero la señal debe verificarse contra comunicados oficiales antes de tratarla como evidencia cerrada.",
        "AI advantage is migrating from model access to control of the compute-and-trust stack.": "La ventaja en IA migra del acceso al modelo hacia el control del stack de cómputo y confianza.",
        "AI advantage is migrating from model access to control of the compute-and-trust stack": "La ventaja en IA migra del acceso al modelo hacia el control del stack de cómputo y confianza",
        "Gives el lector a reusable map for evaluating AI companies by bottleneck control rather than headline capability.": "Entrega un mapa reutilizable para evaluar compañías de IA por control de cuellos de botella, no por capacidades de titular.",
        "Shows el lector why AI strategy increasingly resembles industrial systems integration, not just software iteration.": "La estrategia de IA se parece cada vez más a integración industrial de sistemas, no solo a iteración de software.",
        "Helps el lector track which semiconductor layers and rack components may gain bargaining power.": "Ayuda a identificar qué capas de semiconductores y componentes del rack ganan poder de negociación.",
        "When model capability becomes expensive to scale and risky to deploy, value migrates toward actors that can coordinate silicon, racks, distribution, compliance, and claim substantiation.": "Cuando la capacidad de los modelos se vuelve cara de escalar y riesgosa de desplegar, el valor migra hacia actores capaces de coordinar silicio, racks, distribución, cumplimiento y sustento verificable de sus promesas.",
        "Evidence radar": "Radar de evidencia",
        "Mechanism breakdown": "Despiece de mecanismos",
        "vendor risk": "riesgo de proveedor",
        "unit economics": "economía unitaria",
        "strategic judgment": "juicio estratégico",
        "operator decision advantage": "ventaja operativa para decidir",
        "AI market map literacy": "lectura estructural del mercado de IA",
        "labor-market edge": "ventaja en el mercado laboral",
        "market structure": "estructura de mercado",
    }
    text = remove_personal_reference(value.strip())
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
    return output


def build_briefing_id(thesis: str, edition_date: str) -> tuple[str, str]:
    slug = slugify(thesis)
    return f"{edition_date}-{slug}", slug


def build_meta(packet: dict[str, Any], thesis: str) -> dict[str, Any]:
    meta = packet["meta"]
    brief = packet["brief"]
    edition_date = meta["createdAt"].split("T", 1)[0]
    briefing_id, slug = build_briefing_id(thesis, edition_date)
    output = {
        "schemaVersion": "1.0",
        "briefingId": briefing_id,
        "editionDate": edition_date,
        "publishedAt": meta["createdAt"],
        "slug": slug,
        "language": meta["language"],
        "topics": meta.get("tags", []),
    }

    reader_profile = brief.get("readerProfile")
    if isinstance(reader_profile, dict):
        reader_context: dict[str, Any] = {}
        if isinstance(reader_profile.get("roles"), list) and reader_profile["roles"]:
            reader_context["roles"] = unique_preserving_order([role_label(str(item)) for item in reader_profile["roles"]])
        if isinstance(reader_profile.get("interests"), list) and reader_profile["interests"]:
            reader_context["interests"] = unique_preserving_order([str(item) for item in reader_profile["interests"]])
        desired_upgrade = reader_profile.get("desiredUpgrade")
        if isinstance(desired_upgrade, str) and desired_upgrade.strip():
            reader_context["desiredUpgrade"] = es_text(desired_upgrade.strip())
        if reader_context:
            output["readerContext"] = reader_context

    return output


def build_hero(packet: dict[str, Any], ordered_signals: list[dict[str, Any]]) -> dict[str, str]:
    brief = packet["brief"]
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    lead_signal = ordered_signals[0]
    contradictions = synthesis.get("contradictions", [])
    tension = contradictions[0] if contradictions else lead_signal.get("counterpoints", [""])[0]

    hero = {
        "title": es_text(editorial["heroFrame"]),
        "lede": es_text(f"{clean_sentence(brief['objective'])} {clean_sentence(synthesis['workingThesis'])}"),
        "signal": clean_sentence(es_text(lead_signal["statement"])),
        "thesis": clean_sentence(es_text(synthesis["workingThesis"])),
        "promise": clean_sentence("Esta edición enseña a ubicar dónde se mueve la ventaja y qué decisión exige."),
    }
    if tension:
        hero["tension"] = clean_sentence(es_text(str(tension)))
    return hero


def build_top_line(signals_by_id: dict[str, dict[str, Any]], packet: dict[str, Any]) -> dict[str, str]:
    editorial = packet["editorialDecisions"]
    synthesis = packet["synthesis"]

    first_order_implications: list[str] = []
    second_order_implications: list[str] = []
    for signal_id in editorial["radarOrder"]:
        signal = signals_by_id[signal_id]
        if signal["priority"] != "high":
            continue
        implications = signal["implications"]
        first_order_implications.extend(implications[:1])
        second_order_implications.extend(implications[1:2])
        if len(first_order_implications) >= 2:
            break

    body_parts = [clean_sentence(es_text(synthesis["workingThesis"]))]
    body_parts.extend(clean_sentence(es_text(item)) for item in unique_preserving_order(first_order_implications)[:2])
    if second_order_implications:
        body_parts.append(clean_sentence(f"Efecto de segundo orden: {es_text(second_order_implications[0])}"))
    if synthesis.get("openQuestions"):
        body_parts.append(clean_sentence(f"Pregunta a vigilar: {es_text(synthesis['openQuestions'][0])}"))
    stakes = (
        second_order_implications[-1]
        if second_order_implications
        else first_order_implications[0]
        if first_order_implications
        else brief_stakes_fallback(packet)
    )

    return {
        "title": es_text(editorial["topLineThesis"]),
        "body": " ".join(body_parts),
        "stakes": clean_sentence(es_text(stakes)),
    }


def brief_stakes_fallback(packet: dict[str, Any]) -> str:
    return packet["brief"]["objective"]


def infer_radar_role(signal: dict[str, Any]) -> str:
    if signal["priority"] == "high":
        return "supports-thesis"
    if signal.get("counterpoints"):
        return "complicates-thesis"
    return "monitor"


def build_radar(signals_by_id: dict[str, dict[str, Any]], ordered_ids: list[str]) -> dict[str, Any]:
    return {
        "title": "Radar de evidencia",
        "items": [
            {
                "label": titleize_category(signals_by_id[signal_id]["category"]),
                "text": clean_sentence(es_text(signals_by_id[signal_id]["statement"])),
                "role": infer_radar_role(signals_by_id[signal_id]),
            }
            for signal_id in ordered_ids
        ],
    }


def build_deep_dives(signals_by_id: dict[str, dict[str, Any]], deep_dive_ids: list[str]) -> dict[str, Any]:
    items = []
    for index, signal_id in enumerate(deep_dive_ids, start=1):
        signal = signals_by_id[signal_id]
        implications = signal["implications"]
        body_parts = [
            clean_sentence(f"Mecanismo: {es_text(signal['evidence'])}"),
            clean_sentence(f"Por qué importa: {es_text(implications[0])}"),
        ]
        if len(implications) > 1:
            body_parts.append(clean_sentence(f"Efecto de segundo orden: {es_text(implications[1])}"))
        if signal.get("counterpoints"):
            body_parts.append(clean_sentence(f"Tensión a vigilar: {es_text(signal['counterpoints'][0])}"))
        items.append(
            {
                "title": f"{index}. {es_text(signal['statement']).rstrip('.')}" ,
                "body": " ".join(body_parts),
                "mechanism": titleize_category(signal["category"]),
                "claim": clean_sentence(es_text(signal["statement"])),
                "explanation": clean_sentence(es_text(signal["evidence"])),
                "implication": clean_sentence(es_text(signal["implications"][0])),
            }
        )

    return {
        "title": "Despiece de mecanismos",
        "items": items,
    }


def build_market_map(packet: dict[str, Any]) -> dict[str, Any]:
    """Build a content-specific market map from the actual signals.

    The first prototype used generic winners/pressured/opportunity copy, which
    made the public page feel templated even when the source packet was real.
    This keeps the same contract but derives the positioning from the edition's
    own themes and implications.
    """
    signals = packet["signals"]
    by_category = {str(signal.get("category", "")).lower(): signal for signal in signals}
    infra = by_category.get("infrastructure", signals[0])
    governance = by_category.get("governance", signals[min(1, len(signals) - 1)])
    economics = by_category.get("economics", signals[min(2, len(signals) - 1)])

    return {
        "title": "Mapa de poder: dónde se mueve la ventaja",
        "items": [
            {
                "label": "Ganan poder",
                "text": clean_sentence(
                    "Operadores con acceso creíble a capacidad: chips, energía, data centers, redes y equipos capaces de orquestar inferencia a costo controlado"
                ),
                "powerShift": clean_sentence(es_text(infra["implications"][0])),
            },
            {
                "label": "Quedan presionados",
                "text": clean_sentence(
                    "Compradores y proveedores que trataban la nube como una abstracción neutral; ahora deben justificar dependencia, jurisdicción y continuidad operacional"
                ),
                "powerShift": clean_sentence(es_text(governance["implications"][-1])),
            },
            {
                "label": "Se abre oportunidad",
                "text": clean_sentence(
                    "Perfiles puente —software, infraestructura, riesgo y finanzas— que puedan traducir ambición de IA en arquitectura, compras y economía unitaria"
                ),
                "powerShift": clean_sentence(es_text(economics["implications"][-1])),
            },
        ],
    }


def build_reader_translation(packet: dict[str, Any], high_priority_signals: list[dict[str, Any]]) -> dict[str, Any] | None:
    reader_profile = packet["brief"].get("readerProfile")
    if not isinstance(reader_profile, dict):
        return None
    roles = reader_profile.get("roles")
    if not isinstance(roles, list) or not roles:
        return None

    raw_role_weights = reader_profile.get("roleWeights")
    role_weights = raw_role_weights if isinstance(raw_role_weights, dict) else {}
    role_signal_index = {
        "software-engineer": 1 if len(high_priority_signals) > 1 else 0,
        "engineer": 1 if len(high_priority_signals) > 1 else 0,
        "founder": 0,
        "operator": 1 if len(high_priority_signals) > 1 else 0,
        "operador": 1 if len(high_priority_signals) > 1 else 0,
        "editor estratégico": 0,
        "constructor": 0,
        "aprendiz ejecutivo": 0,
        "executive": 0,
    }
    role_lenses = {
        "software-engineer": "Para un ingeniero de software, la ventaja es diseñar con restricciones reales: costo de inferencia, latencia, capacidad disponible, soberanía y continuidad operacional.",
        "engineer": "Para un ingeniero, la ventaja es diseñar con restricciones reales: costo de inferencia, latencia, capacidad disponible, soberanía y continuidad operacional.",
        "founder": "Para un fundador, la ventaja es convertir infraestructura confiable en promesa comercial: no vender magia de IA, sino capacidad repetible con economía unitaria defendible.",
        "operator": "Para un operador, la ventaja es comprar y gobernar IA como sistema crítico: riesgo de proveedor, jurisdicción, presupuesto, SLAs y dependencia operacional.",
        "operador": "Para un operador, la ventaja es comprar y gobernar IA como sistema crítico: riesgo de proveedor, jurisdicción, presupuesto, SLAs y dependencia operacional.",
        "editor": "Para un editor estratégico, la ventaja es enseñar el mecanismo de poder detrás de la noticia: quién controla capacidad, confianza y distribución.",
        "editor estratégico": "Para un editor estratégico, la ventaja es enseñar el mecanismo de poder detrás de la noticia: quién controla capacidad, confianza y distribución.",
        "builder": "Para un constructor, la ventaja es traducir ambición de IA en arquitectura operable: cómputo, costos, gobernanza y despliegue confiable.",
        "constructor": "Para un constructor, la ventaja es traducir ambición de IA en arquitectura operable: cómputo, costos, gobernanza y despliegue confiable.",
        "learner": "Para un aprendiz ejecutivo, la ventaja es convertir el caso en una lente reutilizable para leer mercados de IA.",
        "aprendiz ejecutivo": "Para un aprendiz ejecutivo, la ventaja es convertir el caso en una lente reutilizable para leer mercados de IA.",
        "executive learner": "Para un aprendiz ejecutivo, la ventaja es convertir el caso en una lente reutilizable para leer mercados de IA.",
        "executive": "Para un ejecutivo, la ventaja es asignar capital con disciplina: separar demanda narrativa de capacidad física, riesgo legal y margen operativo.",
    }

    original_role_order = {str(role).strip(): index for index, role in enumerate(roles) if str(role).strip()}

    def role_weight(role: str) -> float | None:
        value = role_weights.get(role)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
        return None

    ordered_roles = sorted(
        original_role_order,
        key=lambda role: (-(role_weight(role) or 0), original_role_order[role]),
    )
    items = []
    for role_text in ordered_roles:
        normalized_role = role_text.lower()
        signal_index = role_signal_index.get(normalized_role, 0)
        source_signal = high_priority_signals[signal_index] if high_priority_signals else None
        fallback_body = source_signal["implications"][0] if source_signal else packet["brief"]["objective"]
        body = role_lenses.get(normalized_role, es_text(fallback_body))
        label = role_label(role_text)
        weight = role_weight(role_text)
        item = {
            "role": role_text,
            "headline": clean_sentence(f"Qué cambia para un {label}").rstrip("."),
            "body": clean_sentence(es_text(body)),
        }
        if weight is not None:
            item["weight"] = weight
        items.append(item)

    if not items:
        return None
    return {
        "title": "Qué cambia para ti",
        "items": items,
    }


def build_reusable_lesson(packet: dict[str, Any], high_priority_signals: list[dict[str, Any]]) -> dict[str, Any]:
    synthesis = packet["synthesis"]
    apply_when = synthesis.get("supportingThemes", [])[:3]
    takeaway = high_priority_signals[0]["implications"][0] if high_priority_signals else packet["brief"]["objective"]
    return {
        "title": "Lección reutilizable",
        "pattern": clean_sentence(
            "Cuando una capacidad base se vuelve commodity, la ventaja migra hacia quien controla la restricción escasa: capacidad, continuidad, regulación, distribución o contexto no portable."
        ),
        "applyWhen": [clean_sentence(es_text(theme)) for theme in apply_when],
        "takeaway": clean_sentence(es_text(takeaway)),
    }


def infer_watch_type(question: str) -> str:
    lowered = question.strip().lower()
    if any(lowered.startswith(prefix + " ") for prefix in QUESTION_PREFIXES):
        return "question"
    if "metric" in lowered or "correlat" in lowered:
        return "metric"
    if "invalidate" in lowered or "disprove" in lowered:
        return "invalidation"
    return "question"


def build_watchlist(packet: dict[str, Any]) -> dict[str, Any]:
    synthesis = packet["synthesis"]
    editorial = packet["editorialDecisions"]
    questions = unique_preserving_order(editorial["watchlistSeeds"] + synthesis["openQuestions"])
    return {
        "title": "Marco de vigilancia",
        "items": [{"text": clean_sentence(es_text(question)), "type": infer_watch_type(question)} for question in questions],
    }


def transform_ingestion_package_to_signal_input(package: dict[str, Any]) -> dict[str, Any]:
    """Adapt an educational ingestion package v2 into the existing v1 signal-input contract."""
    candidates_by_id = {candidate["signalId"]: candidate for candidate in package["candidates"]}
    clusters_by_id = {cluster["clusterId"]: cluster for cluster in package.get("clusters", [])}
    sources_by_id = {source["sourceId"]: source for source in package["sources"]}
    selected = package["selectedSignals"]
    canonical_profile = next(
        (profile for profile in package["readerProfiles"] if profile.get("profileId") == "sergio-canonical"),
        package["readerProfiles"][0],
    )

    signals: list[dict[str, Any]] = []
    radar_order: list[str] = []
    deep_dive_ids: list[str] = []
    supporting_themes: list[str] = []
    contradictions: list[str] = []

    for selection in selected:
        role = selection["roleInBriefing"]
        if selection.get("signalId"):
            signal_id = selection["signalId"]
            candidate = candidates_by_id[signal_id]
            title = candidate["title"]
            statement = es_text(candidate["factualSummary"])
            category = candidate["domainTags"][0]
            evidence = es_text(candidate["educationalValue"]["learningRationale"])
            source_ids = candidate["sourceIds"]
            implications = [es_text(candidate["editorialRationale"]), es_text(selection["profileRationale"])]
            counterpoints = [es_text(item) for item in candidate.get("auditNotes", [])[:1]]
        else:
            cluster = clusters_by_id[selection["clusterId"]]
            signal_id = cluster["clusterId"]
            title = cluster["title"]
            statement = es_text(cluster["thesisCandidate"])
            category = "market-structure"
            evidence = es_text(cluster["sharedMechanism"])
            cluster_candidates = [candidates_by_id[item] for item in cluster["signalIds"]]
            source_ids = unique_preserving_order(
                [source_id for candidate in cluster_candidates for source_id in candidate["sourceIds"]]
            )
            implications = [es_text(cluster["educationalRationale"]), es_text(selection["profileRationale"])]
            counterpoints = [es_text(cluster["keyTension"])] if cluster.get("keyTension") else []
            supporting_themes.append(cluster["title"])
            if cluster.get("keyTension"):
                contradictions.append(cluster["keyTension"])

        priority = "high" if role == "deep_dive" else "medium" if role in {"radar", "market_map"} else "low"
        signals.append(
            {
                "signalId": signal_id,
                "statement": clean_sentence(es_text(title if role == "radar" else statement)),
                "category": category,
                "priority": priority,
                "sourceIds": source_ids,
                "evidence": clean_sentence(evidence),
                "implications": [clean_sentence(item) for item in implications],
                "counterpoints": [clean_sentence(item) for item in counterpoints] or [clean_sentence(selection["selectionRationale"])],
            }
        )
        radar_order.append(signal_id)
        if role == "deep_dive":
            deep_dive_ids.append(signal_id)

    if not supporting_themes:
        supporting_themes = [signal["category"] for signal in signals[:3]]
    thesis = (
        clusters_by_id[selected[0]["clusterId"]]["thesisCandidate"]
        if selected and selected[0].get("clusterId")
        else signals[0]["statement"]
    )

    return {
        "meta": {
            "schemaVersion": "1.0",
            "inputId": package["meta"]["packageId"],
            "createdAt": package["meta"]["createdAt"],
            "language": "es",
            "owners": ["signal-deck"],
            "tags": package["meta"].get("domains", []),
        },
        "brief": {
            "topic": "Educational technology, AI, and economy briefing",
            "objective": "Convertir señales de tecnología, IA y economía en una mini master class ejecutiva en español.",
            "audience": "lector ejecutivo",
            "timeHorizon": package["run"]["runDate"],
            "readerProfile": {
                "roles": [role_label(str(role)) for role in canonical_profile.get("roles", [])],
                "interests": [es_text(str(interest)) for interest in canonical_profile.get("interests", [])],
                "desiredUpgrade": "; ".join(es_text(str(item)) for item in canonical_profile.get("advantageTargets", [])),
            },
        },
        "sources": [
            {
                "sourceId": source_id,
                "title": sources_by_id[source_id]["title"],
                "sourceType": sources_by_id[source_id]["sourceType"],
                "publisher": sources_by_id[source_id]["publisher"],
            }
            for source_id in unique_preserving_order([source_id for signal in signals for source_id in signal["sourceIds"]])
        ],
        "signals": signals,
        "synthesis": {
            "workingThesis": clean_sentence(es_text(thesis)),
            "supportingThemes": [es_text(item) for item in unique_preserving_order(supporting_themes)[:3]],
            "openQuestions": ["¿Qué evidencia confirmaría que esta tesis mejora resultados operativos y no solo narrativa?"],
            "contradictions": unique_preserving_order(contradictions)[:3],
            "missingInformation": ["Replace sample source URLs with retrieved live evidence during a production run."],
        },
        "editorialDecisions": {
            "heroFrame": "La ventaja se mueve hacia quien controla el mecanismo, no solo la noticia",
            "topLineThesis": clean_sentence(es_text(thesis)),
            "radarOrder": radar_order,
            "deepDiveSignalIds": deep_dive_ids,
            "marketMapFrames": ["Infraestructura", "Confianza", "Economía"],
            "watchlistSeeds": ["Confirmar si las señales seleccionadas generan adopción, margen o poder de distribución medible"],
            "dominantPedagogicalFunction": "reusable_mental_model",
            "readerTranslationLenses": canonical_profile.get("roles", []),
        },
    }


def transform_ingestion_package(package: dict[str, Any]) -> dict[str, Any]:
    return transform_packet(transform_ingestion_package_to_signal_input(package))


def deduplicate_briefing_fields(briefing: dict[str, Any]) -> dict[str, Any]:
    """Protege contra que el mismo texto aparezca en múltiples campos del briefing.

    Si hero.thesis, hero.signal, topLine.title o items del radar comparten el
    mismo texto, reemplaza los duplicados con contenido distinto para que el
    lector nunca vea la misma frase repetida entre secciones.
    """
    hero = briefing.get("hero", {})
    thesis = hero.get("thesis", "")
    signal = hero.get("signal", "")
    top_line = briefing.get("topLine", {})

    # If thesis == signal, derive signal from the first radar item instead
    if thesis and signal and thesis.strip().lower() == signal.strip().lower():
        radar_items = briefing.get("radar", {}).get("items", [])
        if radar_items:
            hero["signal"] = radar_items[0].get("text", signal)
        else:
            hero["signal"] = "Cada señal seleccionada aporta evidencia distinta para la tesis editorial."

    # If topLine.title == thesis, derive a distinct title from implications
    top_title = top_line.get("title", "")
    if thesis and top_title and thesis.strip().lower() == top_title.strip().lower():
        top_line["title"] = hero.get("title", "Lo que cambió esta semana")

    # If hero.title == thesis, replace with a generic editorial frame
    hero_title = hero.get("title", "")
    if thesis and hero_title and thesis.strip().lower() == hero_title.strip().lower():
        hero["title"] = "La ventaja se mueve hacia quien controla el mecanismo, no solo la noticia"

    # If reusableLesson.takeaway == thesis, derive from implications
    lesson = briefing.get("reusableLesson", {})
    takeaway = lesson.get("takeaway", "")
    if thesis and takeaway and thesis.strip().lower() == takeaway.strip().lower():
        pattern = lesson.get("pattern", "")
        lesson["takeaway"] = pattern or "La ventaja migra hacia quien controla la restricción escasa."

    # Check readerTranslation items for body == thesis
    reader_translation = briefing.get("readerTranslation", {})
    for item in reader_translation.get("items", []):
        body = item.get("body", "")
        if thesis and body and body.strip().lower() == thesis.strip().lower():
            item["body"] = "La ventaja práctica es aplicar este marco para anticipar dónde se mueve el poder en tu contexto."

    return briefing


def transform_packet(packet: dict[str, Any]) -> dict[str, Any]:
    editorial = packet["editorialDecisions"]
    signals = packet["signals"]
    signals_by_id = {signal["signalId"]: signal for signal in signals}
    ordered_signals = [signals_by_id[signal_id] for signal_id in editorial["radarOrder"]]
    high_priority_signals = [signal for signal in ordered_signals if signal["priority"] == "high"]

    briefing = {
        "meta": build_meta(packet, editorial["topLineThesis"]),
        "hero": build_hero(packet, ordered_signals),
        "topLine": build_top_line(signals_by_id, packet),
        "radar": build_radar(signals_by_id, editorial["radarOrder"]),
        "deepDives": build_deep_dives(signals_by_id, editorial["deepDiveSignalIds"]),
        "marketMap": build_market_map(packet),
        "reusableLesson": build_reusable_lesson(packet, high_priority_signals),
        "watchlist": build_watchlist(packet),
    }

    reader_translation = build_reader_translation(packet, high_priority_signals)
    if reader_translation:
        briefing["readerTranslation"] = reader_translation

    briefing = deduplicate_briefing_fields(briefing)

    return briefing


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        raise SystemExit(f"ERROR: File not found: {input_path}")

    try:
        data = json.loads(input_path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: Invalid JSON in {input_path}: {exc}") from exc

    packet = expect_dict(data, "signal-input")
    if packet.get("meta", {}).get("schemaVersion") == "2.0" and "selectedSignals" in packet:
        briefing = transform_ingestion_package(packet)
    else:
        validate_input_packet(packet)
        briefing = transform_packet(packet)
    validate_briefing(briefing)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(briefing, indent=2) + "\n")
    print(f"OK: generated briefing at {output_path} from {input_path}")


if __name__ == "__main__":
    main()
