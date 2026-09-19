"""Conservative, evidence-preserving resume extraction; no provider call required."""
import hashlib
import io
import re
from urllib.parse import urlsplit
import zipfile
from xml.etree import ElementTree
import pypdf

from app.rag.chunker import RecursiveTextChunker
from app.rag.parsers import parse_document

EXTRACTOR_VERSION = "1"
SKILL_ALIASES = {
    "Python": (), "JavaScript": ("javascript",), "TypeScript": (),
    "Java": (), "C++": ("cpp",), "C#": ("csharp",), "C": (),
    "SQL": (), "PostgreSQL": ("postgres",), "MySQL": (), "SQLite": (),
    "MongoDB": (), "Redis": (), "HTML": ("html5",), "CSS": ("css3",),
    "React": ("react.js", "reactjs"), "Next.js": ("nextjs",),
    "Node.js": ("nodejs", "node js"), "Express": ("express.js",),
    "Angular": (), "Vue": ("vue.js",), "Django": (), "Flask": (),
    "FastAPI": (), "Spring Boot": (), ".NET": ("dotnet",),
    "Git": (), "GitHub": (), "Docker": (), "Kubernetes": ("k8s",),
    "Linux": (), "AWS": ("amazon web services",), "Azure": (),
    "GCP": ("google cloud",), "REST API": ("restful", "rest apis"),
    "GraphQL": (), "CI/CD": (), "Terraform": (), "Jenkins": (),
    "Machine Learning": (), "Deep Learning": (), "NLP": ("natural language processing",),
    "RAG": ("retrieval augmented generation", "retrieval-augmented generation"),
    "LLM": ("large language model", "llms"), "TensorFlow": (), "PyTorch": (),
    "Pandas": (), "NumPy": (), "Scikit-learn": ("sklearn",),
    "Data Analysis": (), "Power BI": (), "Tableau": (), "Excel": (),
    "Figma": (), "UI/UX": (), "Flutter": (), "Dart": (), "Kotlin": (),
    "Swift": (), "Go": ("golang",), "Rust": (), "PHP": (), "Laravel": (),
    "Communication": (), "Leadership": (), "Teamwork": (), "Problem Solving": (),
}
HEADINGS = {
    "education": r"education|academic(?: qualifications| background)?|qualifications",
    "experience": r"(?:work |professional )?experience|internships?|employment",
    "projects": r"(?:academic |personal |selected )?projects?",
    "skills": r"(?:technical |core |professional )?skills|technologies|technical expertise",
    "certifications": r"certifications?|certificates|licenses",
    "achievements": r"achievements?|awards|honou?rs",
    "summary": r"(?:professional |career )?summary|profile|objective|about me",
}


def safe_url(value: str | None) -> str | None:
    if not value or len(value) > 2000:
        return None
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme.lower() in {"http", "https"} and parsed.hostname and not parsed.username and not parsed.password:
            return value.strip()
    except ValueError:
        pass
    return None


def canonical_skill(name: str) -> str:
    return next((key for key, aliases in SKILL_ALIASES.items() if name.casefold() in {key.casefold(), *(alias.casefold() for alias in aliases)}), name.strip())


def skill_pattern(name: str) -> re.Pattern:
    canonical = canonical_skill(name)
    choices = [canonical, *SKILL_ALIASES.get(canonical, ())]
    # Keep C, C++, C#, Java and JavaScript distinct.
    return re.compile(r"(?<![\w+#])(?:" + "|".join(re.escape(x) for x in choices) + r")(?![\w+#])", re.I)


def skill_evidence(name: str, chunks: list[dict]) -> dict | None:
    pattern = skill_pattern(name)
    for chunk in chunks:
        for line in chunk["content"].splitlines():
            searchable = re.sub(r"https?://\S+|www\.\S+|[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "", line)
            match = pattern.search(searchable)
            if not match:
                continue
            # Explicitly negative/aspirational mentions do not establish coverage.
            prefix = searchable[:match.start()]
            if re.search(r"\b(?:no|not|without|lack|lacking|unfamiliar|want to learn|plan to learn|planning to learn)\b", prefix, re.I):
                continue
            if re.search(r"(?:^|\bcurrently\s+)learning\s*$", prefix, re.I):
                continue
            return {"chunk_id": chunk["chunk_id"], "page_number": chunk.get("page_number"), "quote": line.strip()[:600]}
    return None


def add_hyperlink_targets(content: bytes, filename: str, parsed) -> None:
    """Keep clickable PDF/DOCX targets as references, without fetching any URL."""
    if filename.lower().endswith(".docx"):
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            rel_path = "word/_rels/document.xml.rels"
            if rel_path not in archive.namelist():
                return
            root = ElementTree.fromstring(archive.read(rel_path))
            urls = [rel.attrib.get("Target") for rel in root if rel.attrib.get("Type", "").endswith("/hyperlink")]
        targets = [(parsed.pages[0], urls)]
    elif filename.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content))
        if reader.is_encrypted:
            reader.decrypt("")
        targets = []
        for page in parsed.pages:
            urls = []
            for annotation in reader.pages[page.page_number - 1].get("/Annots", []):
                action = annotation.get_object().get("/A")
                if action:
                    urls.append(action.get_object().get("/URI"))
            targets.append((page, urls))
    else:
        return
    for page, urls in targets:
        for value in list(dict.fromkeys(str(url) for url in urls if url))[:100]:
            url = safe_url(value)
            if url and url not in page.text:
                page.text += "\nSaved link (target only; content not fetched): " + url


def extract_resume(content: bytes, filename: str, document_id: str, catalog: list[str]) -> tuple[dict, list[dict]]:
    if filename.lower().endswith(".doc"):
        raise ValueError("This resume uses the older DOC format. Save it as PDF or DOCX and upload it again.")
    parsed = parse_document(content, filename, document_id)
    link_warning = None
    try:
        add_hyperlink_targets(content, filename, parsed)
    except Exception:
        link_warning = "Some embedded link targets could not be read; visible text links are still available."
    full_text = "\n\n".join(page.text for page in parsed.pages)
    if len(full_text) > 250_000 or parsed.total_pages > 100:
        raise ValueError("This document is too long for resume analysis. Upload a resume of at most 100 pages and 250,000 text characters.")
    chunks = [chunk.model_dump() for chunk in RecursiveTextChunker(900, 120).chunk_document(parsed)]
    names = {name.casefold(): name for name in SKILL_ALIASES}
    names.update({canonical_skill(name).casefold(): canonical_skill(name) for name in catalog if name.strip()})
    skills = []
    for name in sorted(names.values(), key=str.casefold):
        evidence = skill_evidence(name, chunks)
        if evidence:
            skills.append({"name": name, "evidence": evidence})
    sections: dict[str, list[dict]] = {}
    active = None
    for page in parsed.pages:
        for line in page.text.splitlines():
            clean = line.strip().strip(":|").strip()
            heading = next((key for key, pattern in HEADINGS.items() if re.fullmatch(pattern, clean, re.I)), None)
            if heading:
                active = heading
                sections.setdefault(active, [])
            elif active and clean:
                sections[active].append({"text": clean, "page_number": page.page_number})
    links = []
    seen = set()
    for chunk in chunks:
        for match in re.findall(r"https?://[^\s<>\"']+", chunk["content"]):
            url = safe_url(match.rstrip(".,);]"))
            if url and url not in seen:
                seen.add(url)
                links.append({"url": url, "chunk_id": chunk["chunk_id"], "page_number": chunk.get("page_number"), "content_fetched": False})
    checks = [
        {"id": "readable", "label": "Readable document text", "passed": True, "detail": f"{len(full_text.split())} words extracted. Visual layout and reading order still need a manual check."},
        {"id": "education", "label": "Education section", "passed": "education" in sections, "detail": "Use a clear Education heading with degree, institution and dates."},
        {"id": "skills", "label": "Recognizable skills", "passed": bool(skills), "detail": "Explicit skill mentions are checked against the skill catalog; this does not verify proficiency."},
        {"id": "projects", "label": "Projects or experience section", "passed": bool({"projects", "experience"} & sections.keys()), "detail": "Describe your contribution under a clear Projects or Experience heading."},
        {"id": "outcomes", "label": "Quantified outcomes", "passed": bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:%|users\b|requests\b|hours\b|seconds\b|records\b|students\b)", full_text, re.I)), "detail": "Where accurate, describe a measurable outcome such as users served or time saved."},
        {"id": "links", "label": "Portfolio or project links", "passed": bool(links), "detail": "Add relevant, working project or portfolio links. Saved links have not been fetched."},
    ]
    complete_text = parsed.file_type != "pdf" or len(parsed.pages) == parsed.total_pages
    return {
        "skills": skills, "sections": sections, "links": links,
        "complete_text": complete_text,
        "warnings": ([link_warning] if link_warning else []) + ([] if complete_text else ["Some PDF pages had no extractable text. Review those pages or upload a text-based copy before relying on missing-skill feedback."]),
        "word_count": len(full_text.split()), "page_count": parsed.total_pages if parsed.file_type == "pdf" else None,
        "quality": {"checks": checks, "passed": sum(c["passed"] for c in checks), "total": len(checks),
                    "label": "Resume quality checklist", "note": "Text-based checks, not an ATS vendor score or a hiring prediction."},
        "content_hash": hashlib.sha256(content).hexdigest(),
    }, chunks
