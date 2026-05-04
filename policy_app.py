import os
import requests
from flask import Flask, request, jsonify, render_template_string
from io import BytesIO

# ── Optional PDF library detection 

_PDF_BACKEND = None   

try:
    import pdfplumber as _pdfplumber_mod
    _PDF_BACKEND = "pdfplumber"
except ImportError:
    _pdfplumber_mod = None

if _PDF_BACKEND is None:
    try:
        import pypdf as _pypdf_mod
        _PDF_BACKEND = "pypdf"
    except ImportError:
        _pypdf_mod = None

if _PDF_BACKEND is None:
    try:
        import PyPDF2 as _PyPDF2_mod
        _PDF_BACKEND = "PyPDF2"
    except ImportError:
        _PyPDF2_mod = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ── API Key Setup 
# Option 2 — Paste directly below:
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "") or "Your_API_Key"

# Model to use 
GROQ_MODEL = "llama-3.3-70b-versatile"


def validate_api_key():
    """Return the Groq API key, or raise a clear error if it is not set."""
    key = GROQ_API_KEY.strip()
    if not key or key == "PASTE_YOUR_GROQ_KEY_HERE":
        raise ValueError(
            "No Groq API key found.\n\n"
            "To fix this:\n"
            "  1. Go to https://console.groq.com and sign up (free, no card needed)\n"
            "  2. Click API Keys → Create API Key\n"
            "  3. Copy the key (starts with gsk_...)\n"
            "  4. Open policy_app.py and paste it where it says PASTE_YOUR_GROQ_KEY_HERE\n"
            "  5. Restart the app"
        )
    if not key.startswith("gsk_"):
        raise ValueError(
            "This doesn't look like a valid Groq API key.\n"
            "Groq keys start with 'gsk_'. Please check your key at https://console.groq.com"
        )
    return key

# ─── Pre-loaded Policy Text: Commercial Bank of Ceylon PLC — Group ESRM Policy (January 2025) ───────
DEFAULT_POLICY_TEXT = """
COMMERCIAL BANK OF CEYLON PLC
GROUP ENVIRONMENTAL AND SOCIAL RISK MANAGEMENT POLICY
Version 3.0 | January 2025
Approved by: Board of Directors on 30.01.2025 | Next Review: January 2026
Responsibility: Integrated Risk Management Department

─────────────────────────────────────────────────────────────
1. INTRODUCTION
─────────────────────────────────────────────────────────────

This policy applies to Commercial Bank of Ceylon PLC operations in Sri Lanka and Bangladesh, and
its subsidiaries in the Maldives, Myanmar, and CBC Finance (collectively referred to as the 'Group').

The Group recognizes Environmental and Social (E&S) risks and opportunities arising from its activities,
which can significantly impact the economies, communities, and environments in which it operates.
To address these, the Group has established an Environmental and Social Risk Management System (ESRMS).

The Group's approach covers two key areas:
- E&S Risk Management within Internal Operations: Identifying, assessing, and mitigating direct
  environmental and social risks from the Group's own facilities and workplace practices.
- E&S Risk Management in Lending: Ensuring all financed projects are environmentally sustainable,
  socially responsible, and economically viable.

─────────────────────────────────────────────────────────────
2. SCOPE
─────────────────────────────────────────────────────────────

This policy encompasses all business activities of the Group and applies to all Branches and
Departments regardless of geographic location.

─────────────────────────────────────────────────────────────
3. GUIDING PRINCIPLES AND STANDARDS
─────────────────────────────────────────────────────────────

The Bank leverages:
- Roadmap for Sustainable Finance in Sri Lanka (CBSL, 2019)
- Banking Act Directions No. 05 of 2022 on Sustainable Finance Activities of Licensed Banks
- Sri Lanka Green Finance Taxonomy 2022
- Banking Act No. 05 of 2024 on Corporate Governance and Licensed Banks
- IFRS/SLFRS S1 (General Sustainability Disclosures) and S2 (Climate-related Disclosures)
- IFC Performance Standards on Environmental and Social Sustainability (January 2012)
- ILO Fundamental Conventions on Labour Rights
- United Nations Global Compact (UNGC) Principles

As a signatory to the Sustainable Banking Principles of Sri Lanka, the Bank works with other local
banks in promoting their adoption.

Bangladesh Operations additionally follow: Guidelines on ESRM for Banks and Financial Institutions
(Bangladesh Bank, 2022); Sustainable Finance Policy for Banks and Financial Institutions (2022);
Guideline on Sustainability and Climate-related Financial Disclosures (2023).

─────────────────────────────────────────────────────────────
4. POLICY STATEMENT — INTERNAL OPERATIONS
─────────────────────────────────────────────────────────────

Environmental Risk Management (Internal):
- Monitoring, evaluating, and setting reduction targets for carbon emissions, resource use,
  and waste production across all operations.
- Promoting eco-efficiency and implementing measures to mitigate environmental risks in
  workplace practices and processes.

Social Risk Management (Internal):
- Upholding ILO Fundamental Conventions (forced labour, freedom of association, collective
  bargaining, equal remuneration, abolition of forced labour, non-discrimination, minimum age,
  and elimination of worst forms of child labour).
- Aligning with IFC Performance Standard-2 on Labour and Working Conditions and UNGC Principles.
- Extending social responsibility to suppliers and business partners through clear performance
  expectations and monitoring.

─────────────────────────────────────────────────────────────
5. POLICY STATEMENT — LENDING / FINANCIAL SERVICES
─────────────────────────────────────────────────────────────

General Lending Principles:
- All projects financed by the Group must comply with this policy and align with the Group's E&S objectives.
- The Group will not knowingly finance projects contravening obligations under relevant international
  agreements, treaties, or conventions.
- Projects in Sri Lanka must comply with all applicable country laws and regulations.
- Projects outside Sri Lanka must comply with host country regulations and the core principles of this policy.
- Projects must be designed, operated, and maintained following best industrial practices.

E&S Risk Assessment and Mitigation:
- All financed projects are subject to systematic E&S risk screening and assessment.
- Mitigation strategies (Avoidance → Minimisation → Remediation → Offset) must be applied before
  or alongside financing for identified risks.
- Particular attention is required for: Involuntary Resettlement, Indigenous Peoples' Rights,
  Significant Biodiversity or Cultural Heritage Impacts, and Occupational Health and Safety risks.

Labour Rights in Lending:
- All financed projects must respect ILO fundamental conventions — no forced labour, no child labour.
- Continuous enhancement of risk tools to identify and mitigate labour-related risks.

Gender and Social Inclusion:
- Gender-specific risks must be identified in project evaluations.
- Preventive and corrective measures must address gender-based violence, abuse, and exploitation.

Circular Economy and Resource Efficiency:
- Projects are encouraged to adopt circular economy principles: reducing virgin material use,
  improving resource efficiency, recycling end-of-life products.
- Customers are encouraged to reduce resource consumption, improve energy and water efficiency.

Health, Safety and Security:
- Customers must implement comprehensive measures to prevent accidents, injuries, and health risks
  for workers and project-affected communities.
- Preventive and protective plans must follow the hierarchy of risk control and recognised good practices.

Biodiversity and Natural Resources:
- Financed projects must minimise impacts on biodiversity and ecological resources across their lifecycle.
- Biodiversity conservation and ecosystem services protection are integral to E&S risk management.

Involuntary Resettlement:
- Proactive risk identification and mitigation (e.g. fair compensation) required for projects involving
  land acquisition or restrictions that could cause physical or economic displacement.

Indigenous Peoples:
- Projects must uphold the dignity, rights, and livelihoods of indigenous communities.
- Ongoing consultation and involvement of indigenous communities throughout a project's lifecycle is required.

Cultural Heritage:
- Customers must adopt a precautionary approach to protect both tangible and intangible cultural heritage.

Climate Risk:
- The Group integrates climate risk assessment into financial decision-making.
- All operations must adhere to the "Do No Significant Harm (DNSH) to the Environment" principle
  per Sri Lanka Green Finance Taxonomy 2022 and Bangladesh Bank Sustainable Finance Policy 2022.

Monitoring and Compliance:
- Each financed project is subject to continuous E&S monitoring proportionate to its scale and risk.
- Customers must provide sufficient information via loan covenants to enable Group risk appraisal.
- Results of E&S appraisals must be included in documentation submitted to approving authorities.
- The Group discloses E&S risk management in annual reports per GRI standards and IFRS/SLFRS S1 and S2.

─────────────────────────────────────────────────────────────
6. BANNED / ILLEGAL ACTIVITIES (ANNEX I — ABSOLUTE EXCLUSIONS)
─────────────────────────────────────────────────────────────

The Group shall NOT finance any of the following:
1. Products/activities illegal under national laws or subject to international phase-outs/bans
   (pharmaceuticals, hazardous chemicals/pesticides, ozone-depleting substances, hazardous waste
   trans-boundary movements, wildlife trade regulated under CITES).
2. Activities prohibited under national/international laws protecting critical cultural and natural heritage.
3. Production or trade in nuclear and radioactive materials (excluding limited medical/research uses).
4. Unsustainable fishing (blast fishing, cyanide fishing, drift nets > 2.5 km in marine environments).
5. Forced labour or harmful child labour (below age 14 per ILO, or higher if required by local law).
6. Production or trade in weapons designed for military purposes, including CBRN weapons.
7. Destruction of critical habitats or protected areas covered under national law; forest clearance
   without a sustainable management plan.
8. Timber/timber products from non-sustainably managed forests.
9. Activities impacting indigenous peoples' lands without documented consent.
10. Pornography and/or prostitution.
11. Coal-related projects (new/existing coal mining, transport, coal-fired power generation, or
    dedicated infrastructure — excluding captive industrial coal-fired plants in cement/chemical sectors).
12. Production or trade in un-bonded asbestos fibres (bonded asbestos cement sheets with < 20%
    asbestos content are excluded).
13. Projects/activities in geographies pre-approved by the Board as having credible reports of
    human rights abuses and limited transparency.

─────────────────────────────────────────────────────────────
7. E&S NEGATIVE LIST (RESTRICTED ACTIVITIES — PORTFOLIO THRESHOLD APPLIES)
─────────────────────────────────────────────────────────────

Aggregate lending to customers in these activities must not exceed a Board-approved portfolio threshold:
1. Production, storing, and selling of alcoholic beverages (excluding beer and wine).
2. Cultivating, processing, storing, and trading of tobacco.
3. Gambling, casinos, horse racing, and equivalent enterprises.
4. Production, transport, storage, trade, and commercial-scale usage of hazardous chemicals
   including petrol, kerosene, and other petroleum products (applicable to micro and small enterprises only).

─────────────────────────────────────────────────────────────
8. GOVERNANCE
─────────────────────────────────────────────────────────────

- Board of Directors: Ultimate responsibility for ESRM oversight; approves Group-wide policy;
  ensures ESRM aligns with each entity's risk appetite and strategic goals.
- Board Integrated Risk Management Committee (BIRMC) and Executive Integrated Risk Management
  Committee (EIRMC): Oversee ESRM policy development, implementation, and monitoring; assess
  significant E&S risks in high-risk sector financing.
- Chief Risk Officer and Senior Management: Ensure ESRM integration into core business strategy;
  provide resources for effective ESRM implementation.
- ESRM Team (within Risk Management Department): Develop and update ESRM policies; conduct
  E&S risk assessments; train staff; engage with regulators and NGOs on evolving ESG standards.

─────────────────────────────────────────────────────────────
9. IMPLEMENTATION AND REVIEW
─────────────────────────────────────────────────────────────

- The Group shall develop, maintain, and implement E&S Risk Assessment and Management Procedures,
  guidance notes, and tools.
- Staff capacity building and training on E&S policy requirements is mandatory.
- A standard procedure for reporting accidents/incidents related to financed project E&S issues is maintained.
- A web-based Project Complaint Mechanism (PCM) is maintained to receive and assess grievances from
  external parties. Corporate Management is informed of events and grievances for appropriate decisions.
- The policy is reviewed annually (or as directed by respective Boards) against updated local and
  international guidelines and standards.
- Responsibility for formulating, reviewing, and amending this policy is vested in the respective
  Integrated Risk Management Departments of Group entities, subject to BOD approval.
""".strip()

# ─── Predefined Scenarios ─────────────────────────────────────────────────────
PREDEFINED_SCENARIOS = [
    {
        "id": "scenario_1",
        "name": "Large-Scale Infrastructure Project",
        "emoji": "🏗️",
        "description": (
            "Adapt the CBC Group ESRM Policy for a large infrastructure project (e.g. highway, "
            "dam, or industrial park) in Sri Lanka seeking significant financing. The project involves "
            "land acquisition, potential involuntary resettlement of affected communities, and substantial "
            "environmental footprint including deforestation and waterway impacts. Assessment must address "
            "IFC Performance Standards (PS1–PS8), biodiversity impacts, community health and safety, "
            "cultural heritage risks, and labour rights in construction. A detailed Environmental and "
            "Social Impact Assessment (ESIA), resettlement action plan, and stakeholder grievance mechanism "
            "are required before financing can proceed. Apply the full mitigation hierarchy."
        ),
        "audience": "Project finance officers, environmental analysts, community relations teams, IRMD"
    },
    {
        "id": "scenario_2",
        "name": "Agribusiness / Plantation Sector Lending",
        "emoji": "🌿",
        "description": (
            "Adapt the CBC Group ESRM Policy for lending to an agribusiness or plantation company "
            "(tea, rubber, palm oil, or large-scale crop cultivation) in Sri Lanka or Bangladesh. "
            "The sector involves elevated risks including pesticide and agrochemical use, deforestation, "
            "water-intensive processes, biodiversity impacts, migrant and seasonal labour vulnerabilities, "
            "child labour risks, and indigenous land rights. The adaptation must specify the E&S screening "
            "criteria, required certifications (e.g. sustainable agriculture standards), acceptable chemical "
            "use policies aligned with the Rotterdam and Stockholm Conventions, and mandatory labour rights "
            "checks. Coal-related energy inputs must be flagged. Portfolio threshold limits apply."
        ),
        "audience": "Agri-finance specialists, environmental risk officers, compliance teams, credit officers"
    },
    {
        "id": "scenario_3",
        "name": "SME Green Finance / Circular Economy Loan",
        "emoji": "♻️",
        "description": (
            "Adapt the CBC Group ESRM Policy for a simplified ESRM framework for small and medium "
            "enterprises (SMEs) applying for green financing or circular economy loans under the Sri Lanka "
            "Green Finance Taxonomy 2022. These businesses may be in manufacturing, waste management, "
            "renewable energy, or resource-efficient production. The framework must apply the 'Do No "
            "Significant Harm' (DNSH) principle, streamlined E&S screening appropriate to the scale of "
            "SME operations, resource efficiency targets, and minimal but adequate reporting requirements. "
            "Include guidance on what qualifies as green/eligible activity versus excluded activity, "
            "referencing both the CBSL Sustainable Finance Roadmap and IFC Performance Standard-1."
        ),
        "audience": "SME relationship managers, green finance officers, sustainability analysts, IRMD"
    },
    {
        "id": "scenario_4",
        "name": "Bangladesh Operations — High-Risk Sector Lending",
        "emoji": "🇧🇩",
        "description": (
            "Adapt the CBC Group ESRM Policy specifically for the Bank's Bangladesh operations, "
            "applying Bangladesh Bank's ESRM Guidelines (2022), Sustainable Finance Policy (2022), and "
            "Climate-related Financial Disclosures Guideline (2023). The scenario involves lending to "
            "a garments/textile or tannery industry borrower — sectors with high labour rights exposure, "
            "chemical effluent discharge risks, and significant water consumption impacts. The adaptation "
            "must integrate Bangladesh Bank's Exclusion List alongside the CBC Group Annex I Banned List, "
            "specify sector-specific E&S risk categorisation, required Environmental Management Plans, "
            "occupational health standards for workers in hazardous conditions, and enhanced monitoring "
            "obligations for high-risk (Category A/B) borrowers."
        ),
        "audience": "Bangladesh branch credit officers, ESG compliance officers, Bangladesh Bank examiners"
    }
]

# ─── HTML Template ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Policy Summarization & Scenario Adaptation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,300&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --navy:#0d1b2a;--deep:#162032;--panel:#1a2840;--card:#1f3050;--border:#2a3f5f;
      --gold:#c9a84c;--gold-light:#e8c97a;--gold-dim:rgba(201,168,76,0.15);
      --green:#4caf82;--green-dim:rgba(76,175,130,0.12);--green-light:#6ecfa0;
      --teal:#4ecdc4;--teal-dim:rgba(78,205,196,0.12);
      --text:#e8eff8;--text-muted:#8fa3be;--text-dim:#5c7a9a;
      --success:#4caf82;--error:#e05a6a;
    }
    html,body{height:100%;background:var(--navy);color:var(--text);font-family:'Source Serif 4',Georgia,serif;font-size:15px;line-height:1.6;overflow:hidden}

    /* ── Header ── */
    header{background:var(--deep);border-bottom:2px solid var(--green);padding:0 2rem;height:64px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 4px 24px rgba(0,0,0,0.5)}
    .brand{display:flex;align-items:center;gap:12px}
    .brand-icon{width:38px;height:38px;background:linear-gradient(135deg,var(--green),var(--green-light));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
    .brand h1{font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--green-light)}
    .brand p{font-size:0.68rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;letter-spacing:1px;text-transform:uppercase}
    .badge{background:rgba(76,175,130,0.15);border:1px solid var(--green);color:var(--green-light);padding:4px 12px;border-radius:20px;font-size:0.72rem;font-family:'JetBrains Mono',monospace}

    /* ── Layout ── */
    .workspace{display:grid;grid-template-columns:1fr 1fr;height:calc(100vh - 64px)}
    .panel{height:100%;overflow-y:auto;padding:1.5rem;background:var(--panel);scrollbar-width:thin;scrollbar-color:var(--border) transparent}
    .panel:first-child{border-right:2px solid var(--border)}
    .panel::-webkit-scrollbar{width:4px}
    .panel::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

    /* ── Panel headers ── */
    .panel-header{display:flex;align-items:center;gap:10px;margin-bottom:1.25rem;padding-bottom:1rem;border-bottom:1px solid var(--border)}
    .panel-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
    .panel-icon.green{background:var(--green-dim)}
    .panel-icon.teal{background:var(--teal-dim)}
    .panel-header h2{font-family:'Playfair Display',serif;font-size:1.1rem}
    .panel-header p{font-size:0.75rem;color:var(--text-muted);margin-top:1px}

    /* ── Cards ── */
    .card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1.1rem;margin-bottom:1rem}
    .card-title{font-family:'JetBrains Mono',monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;color:var(--text-muted);margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between}

    /* ── Form elements ── */
    label{display:block;font-size:0.78rem;color:var(--text-muted);margin-bottom:4px;font-family:'JetBrains Mono',monospace}
    textarea,select,input[type=text]{width:100%;background:var(--navy);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Source Serif 4',serif;font-size:0.83rem;padding:0.65rem 0.75rem;transition:border-color 0.2s;resize:vertical}
    textarea:focus,select:focus,input[type=text]:focus{outline:none;border-color:var(--green)}
    input[type=text]{resize:none}

    /* ── Tabs ── */
    .tab-row{display:flex;gap:4px;margin-bottom:0.75rem;background:var(--navy);padding:4px;border-radius:8px}
    .tab-btn{flex:1;padding:0.4rem;border:none;border-radius:6px;background:transparent;color:var(--text-muted);font-size:0.73rem;font-family:'JetBrains Mono',monospace;cursor:pointer;transition:all 0.2s;letter-spacing:0.5px}
    .tab-btn.active{background:var(--card);color:var(--green-light)}
    .tab-content{display:none}
    .tab-content.active{display:block}

    /* ── Upload zone ── */
    .upload-zone{border:2px dashed var(--border);border-radius:8px;padding:1.2rem;text-align:center;cursor:pointer;transition:all 0.2s;background:var(--navy);margin-bottom:0.75rem}
    .upload-zone:hover,.upload-zone.drag-over{border-color:var(--green);background:var(--green-dim)}
    .upload-zone span{font-size:1.5rem;display:block;margin-bottom:4px}
    .upload-zone p{font-size:0.79rem;color:var(--text-muted)}
    #fileInput{display:none}

    /* ── Buttons ── */
    .btn{display:inline-flex;align-items:center;gap:7px;padding:0.55rem 1rem;border:none;border-radius:7px;font-size:0.8rem;font-family:'JetBrains Mono',monospace;cursor:pointer;transition:all 0.2s;letter-spacing:0.3px}
    .btn-green{background:linear-gradient(135deg,var(--green),#3a9a6a);color:#fff;font-weight:600}
    .btn-green:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(76,175,130,0.35)}
    .btn-teal{background:linear-gradient(135deg,var(--teal),#3ab5ac);color:var(--navy);font-weight:600}
    .btn-teal:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(78,205,196,0.3)}
    .btn-ghost{background:transparent;border:1px solid var(--border);color:var(--text-muted)}
    .btn-ghost:hover{border-color:var(--text-muted);color:var(--text)}
    .btn:disabled{opacity:0.45;cursor:not-allowed;transform:none!important}
    .btn-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:0.75rem}
    .btn-full{width:100%;justify-content:center;padding:0.7rem}

    /* ── Scenario chips ── */
    .scenario-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:0.75rem}
    .chip{background:var(--navy);border:1.5px solid var(--border);border-radius:8px;padding:0.7rem;cursor:pointer;transition:all 0.2s}
    .chip:hover{border-color:var(--teal);background:var(--teal-dim)}
    .chip.selected{border-color:var(--teal);background:var(--teal-dim)}
    .chip-title{font-weight:600;color:var(--text);font-size:0.82rem;margin-bottom:2px}
    .chip-sub{color:var(--text-muted);font-size:0.7rem;line-height:1.3}

    /* ── Status bars ── */
    .status{display:flex;align-items:flex-start;gap:8px;padding:0.5rem 0.8rem;border-radius:6px;font-size:0.77rem;font-family:'JetBrains Mono',monospace;margin-bottom:0.75rem;animation:fadeIn 0.3s ease;white-space:pre-wrap;word-break:break-word;line-height:1.5}
    .status.loading{background:rgba(76,175,130,0.1);border:1px solid rgba(76,175,130,0.3);color:var(--green-light)}
    .status.success{background:rgba(76,175,130,0.1);border:1px solid rgba(76,175,130,0.3);color:var(--success)}
    .status.error{background:rgba(224,90,106,0.1);border:1px solid rgba(224,90,106,0.3);color:var(--error)}
    .spinner{width:13px;height:13px;border:2px solid transparent;border-top-color:var(--green);border-radius:50%;animation:spin 0.8s linear infinite;flex-shrink:0}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}

    /* ── Output box ── */
    .output-box{background:var(--navy);border:1px solid var(--border);border-radius:8px;padding:1rem;min-height:150px;font-size:0.82rem;line-height:1.75;color:var(--text)}
    .output-box h2{font-family:'Playfair Display',serif;color:var(--green-light);font-size:0.95rem;margin:0.8rem 0 0.3rem;border-bottom:1px solid var(--border);padding-bottom:3px}
    .output-box h3{color:var(--teal);font-size:0.82rem;margin:0.5rem 0 0.2rem;font-family:'JetBrains Mono',monospace}
    .output-box strong{color:var(--green-light)}
    .output-box ul{padding-left:1.2rem;margin:0.3rem 0}
    .output-box li{margin-bottom:0.2rem}

    /* ── Draft cards ── */
    .draft-card{background:var(--navy);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:1rem}
    .draft-header{background:var(--card);padding:0.65rem 1rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)}
    .draft-title{font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:var(--teal)}
    .draft-body{padding:1rem;font-size:0.82rem;line-height:1.75;color:var(--text);max-height:520px;overflow-y:auto}

    /* ── Copy button ── */
    .copy-btn{background:transparent;border:1px solid var(--border);border-radius:5px;color:var(--text-muted);font-size:0.7rem;font-family:'JetBrains Mono',monospace;padding:3px 8px;cursor:pointer;transition:all 0.2s}
    .copy-btn:hover{border-color:var(--teal);color:var(--teal)}

    /* ── Divider ── */
    .divider{display:flex;align-items:center;gap:8px;margin:0.75rem 0;color:var(--text-dim);font-size:0.7rem;font-family:'JetBrains Mono',monospace}
    .divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border)}

    /* ── Char count ── */
    .char-count{text-align:right;font-size:0.67rem;font-family:'JetBrains Mono',monospace;color:var(--text-dim);margin-top:3px}

    /* ── Empty state ── */
    .empty-state{text-align:center;padding:2.5rem 1rem;color:var(--text-dim);font-style:italic;font-size:0.85rem}
    .empty-state .icon{font-size:2.2rem;display:block;margin-bottom:0.5rem}

    /* ── Helper ── */
    .mb{margin-bottom:0.6rem}

    /* ── Responsive ── */
    @media(max-width:860px){
      .workspace{grid-template-columns:1fr;height:auto;overflow-y:auto}
      .panel{height:auto;overflow-y:visible}
      html,body{overflow:auto}
      .scenario-grid{grid-template-columns:1fr}
    }
  </style>
</head>
<body>

<header>
  <div class="brand">
    <div class="brand-icon">🔒</div>
    <div>
      <h1>Policy Summarization & Scenario Adaptation</h1>
    </div>
  </div>
  <div class="badge">⚡ Powered by Groq AI (Free)</div>
</header>

<div class="workspace">

  <!-- ══════ LEFT PANEL — POLICY SUMMARISATION ══════ -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-icon green">📄</div>
      <div>
        <h2>Policy Summarisation</h2>
        <p>Upload, paste, or use the pre-loaded CBC ESRM Policy — then generate an AI summary covering goals, risk areas &amp; governance</p>
      </div>
    </div>

    <!-- Input source tabs -->
    <div class="card">
      <div class="card-title">📥 POLICY INPUT SOURCE</div>
      <div class="tab-row">
        <button class="tab-btn active" onclick="switchTab('upload', event)">📎 Upload PDF</button>
        <button class="tab-btn" onclick="switchTab('paste', event)">📝 Paste Text</button>
        <button class="tab-btn" onclick="switchTab('preload', event)">🏛️ Pre-loaded</button>
      </div>

      <!-- Upload tab -->
      <div id="tab-upload" class="tab-content active">
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
          <span>📂</span>
          <p><strong>Click to upload</strong> or drag &amp; drop a PDF</p>
          <p style="font-size:0.7rem;margin-top:4px;color:var(--text-dim)">PDF files up to 16MB</p>
        </div>
        <input type="file" id="fileInput" accept=".pdf" onchange="handleFile(event)">
        <div id="uploadStatus"></div>
      </div>

      <!-- Paste tab -->
      <div id="tab-paste" class="tab-content">
        <label>Paste policy text below:</label>
        <textarea id="pasteText" rows="7" placeholder="Paste your ESRM policy or any E&amp;S risk management policy document text here..."
          oninput="document.getElementById('pasteChars').textContent=this.value.length.toLocaleString()"></textarea>
        <div class="char-count"><span id="pasteChars">0</span> characters</div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="usePasteText()">✓ Use This Text</button>
          <button class="btn btn-ghost" onclick="document.getElementById('pasteText').value='';document.getElementById('pasteChars').textContent='0'">✕ Clear</button>
        </div>
      </div>

      <!-- Pre-loaded tab -->
      <div id="tab-preload" class="tab-content">
        <div style="background:var(--navy);border-radius:8px;padding:0.85rem;margin-bottom:0.75rem">
          <p style="font-size:0.82rem;color:var(--green-light);font-weight:600;margin-bottom:4px">🌿 Pre-loaded ESRM policy ready</p>
          <p style="font-size:0.75rem;color:var(--text-muted)">Commercial Bank of Ceylon PLC — Group ESRM Policy v3.0 (January 2025)</p>
          <p style="font-size:0.7rem;color:var(--text-dim);margin-top:3px;font-family:'JetBrains Mono',monospace">Lending Risk · Banned Activities · E&amp;S Screening · Governance · IFC Standards</p>
        </div>
        <button class="btn btn-green" onclick="loadDefault()">🌿 Load CBC ESRM Policy</button>
      </div>
    </div>

    <!-- Active policy preview -->
    <div class="card" id="previewCard" style="display:none">
      <div class="card-title">
        <span>📋 ACTIVE POLICY TEXT (editable)</span>
        <button class="copy-btn" onclick="copyEl('activeText')">Copy</button>
      </div>
      <textarea id="activeText" rows="5"
        oninput="activePolicyText=this.value;document.getElementById('activeChars').textContent=this.value.length.toLocaleString()"></textarea>
      <div class="char-count"><span id="activeChars">0</span> characters loaded</div>
    </div>

    <!-- Generate summary button -->
    <div id="sumStatus"></div>
    <button class="btn btn-green btn-full" id="sumBtn" onclick="generateSummary()" disabled>
      🔍 Generate Policy Summary
    </button>

    <!-- Summary output -->
    <div class="card" id="summaryCard" style="margin-top:1rem;display:none">
      <div class="card-title">
        <span>📊 AI-GENERATED SUMMARY</span>
        <div style="display:flex;gap:6px">
          <button class="copy-btn" onclick="copyEl('summaryOut')">Copy</button>
          <button class="copy-btn" style="color:var(--teal);border-color:var(--teal)"
            onclick="document.getElementById('rightPanel').scrollIntoView({behavior:'smooth'})">→ Scenarios</button>
        </div>
      </div>
      <div class="output-box" id="summaryOut"></div>
    </div>
  </div>

  <!-- ══════ RIGHT PANEL — SCENARIO GENERATION ══════ -->
  <div class="panel" id="rightPanel">
    <div class="panel-header">
      <div class="panel-icon teal">🎭</div>
      <div>
        <h2>Scenario-Based Policy Generation</h2>
        <p>Select one or more lending/sector scenarios and generate adapted ESRM policy frameworks from the summary</p>
      </div>
    </div>

    <!-- Scenario selector -->
    <div class="card">
      <div class="card-title">🎯 SELECT PREDEFINED SCENARIOS</div>
      <p style="font-size:0.78rem;color:var(--text-muted);margin-bottom:0.75rem">
        Each scenario adapts the ESRM policy for a specific lending context, sector, or jurisdiction. Select one or more, then click Generate.
      </p>
      <div class="scenario-grid" id="scenarioGrid">
        {% for s in scenarios %}
        <div class="chip" id="chip-{{ s.id }}" onclick="toggleChip('{{ s.id }}')">
          <div class="chip-title">{{ s.emoji }} {{ s.name }}</div>
          <div class="chip-sub">{{ s.audience }}</div>
        </div>
        {% endfor %}
      </div>

      <div class="divider">OR DEFINE A CUSTOM SCENARIO</div>

      <label class="mb">Custom Scenario Name:</label>
      <input type="text" id="customName" placeholder="e.g., Renewable Energy / Solar Project Financing" class="mb" style="margin-bottom:0.6rem">

      <label class="mb">Custom Scenario Description:</label>
      <textarea id="customDesc" rows="3"
        placeholder="Describe the lending context, sector, borrower profile, and key E&S risk priorities for this scenario..." class="mb"></textarea>

      <label style="margin-top:0.4rem">Additional Requirements (optional):</label>
      <textarea id="customReqs" rows="2" placeholder="Any specific constraints, regulations, or emphasis areas..."></textarea>
    </div>

    <!-- Summary readiness indicator -->
    <div class="card">
      <div class="card-title">📋 SUMMARY STATUS</div>
      <div id="summaryStatus" style="font-size:0.8rem;color:var(--text-muted);font-style:italic">
        ⚠️ No summary yet — generate a summary in the left panel first.
      </div>
    </div>

    <!-- Generate & clear buttons -->
    <div id="genStatus"></div>
    <div style="display:flex;gap:8px;margin-bottom:1rem">
      <button class="btn btn-teal btn-full" id="genBtn" onclick="generateScenarios()" disabled style="flex:1">
        ⚡ Generate Selected Scenarios
      </button>
      <button class="btn btn-ghost" onclick="clearDrafts()" title="Clear all drafts" style="padding:0.7rem 0.9rem">✕</button>
    </div>

    <!-- Draft outputs -->
    <div id="draftsContainer">
      <div class="empty-state">
        <span class="icon">📜</span>
        <p>Adapted policy drafts will appear here.</p>
        <p style="font-size:0.75rem;margin-top:0.3rem">Select scenarios above and click <strong>Generate</strong>.</p>
        <p style="font-size:0.72rem;margin-top:0.5rem;color:var(--text-dim)">You can change scenarios and regenerate at any time.</p>
      </div>
    </div>
  </div>

</div><!-- /workspace -->

<script>
  // ── State ──────────────────────────────────────────────────────────────────
  let activePolicyText = '';
  let activeSummary = '';
  let selectedScenarios = {};

  const SCENARIO_DATA = {
    {% for s in scenarios %}
    '{{ s.id }}': {
      name: '{{ s.emoji }} {{ s.name }}',
      description: `{{ s.description }}`
    },
    {% endfor %}
  };

  // ── Tabs ───────────────────────────────────────────────────────────────────
  function switchTab(name, evt) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    evt.currentTarget.classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
  }

  // ── File upload ────────────────────────────────────────────────────────────
  const zone = document.getElementById('uploadZone');
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
  });

  function handleFile(e) { if (e.target.files[0]) processFile(e.target.files[0]); }

  async function processFile(file) {
    showStatus('uploadStatus', 'loading', `⏳ Extracting text from "${file.name}"...`);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch('/api/extract-pdf', { method: 'POST', body: fd });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      setPolicy(d.text);
      const backend = d.backend ? ` (via ${d.backend})` : '';
      showStatus('uploadStatus', 'success', `✓ Extracted ${d.chars.toLocaleString()} characters from "${file.name}"${backend}`);
    } catch (e) {
      // Show the full error message — it may contain install instructions
      const msg = e.message || 'Unknown error. Is the Flask server running?';
      showStatus('uploadStatus', 'error', `✕ ${msg}`);
    }
  }

  // ── Paste / Default ────────────────────────────────────────────────────────
  function usePasteText() {
    const t = document.getElementById('pasteText').value.trim();
    if (!t) { alert('Please paste some text first.'); return; }
    setPolicy(t);
  }

  function loadDefault() {
    setPolicy({{ default_policy | tojson }});
    showStatus('uploadStatus', 'success', '✓ CBC Group ESRM Policy (v3.0, Jan 2025) loaded successfully');
  }

  function setPolicy(text) {
    activePolicyText = text;
    document.getElementById('activeText').value = text;
    document.getElementById('activeChars').textContent = text.length.toLocaleString();
    document.getElementById('previewCard').style.display = 'block';
    document.getElementById('sumBtn').disabled = false;
  }

  // ── Summarisation ──────────────────────────────────────────────────────────
  async function generateSummary() {
    if (!activePolicyText) { alert('No policy text loaded.'); return; }
    showStatus('sumStatus', 'loading', '🔍 Analysing ESRM policy — this may take 20–40 seconds...');
    document.getElementById('sumBtn').disabled = true;
    // Reset summary status on right panel
    updateSummaryStatus(false);
    try {
      const r = await fetch('/api/summarise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy_text: activePolicyText })
      });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      activeSummary = d.summary;
      renderSummary(d.summary);
      showStatus('sumStatus', 'success', '✓ Summary generated — ready for scenario generation');
      updateSummaryStatus(true);
    } catch (e) {
      showStatus('sumStatus', 'error', `✕ ${e.message}`);
    } finally {
      document.getElementById('sumBtn').disabled = false;
    }
  }

  function renderSummary(text) {
    const card = document.getElementById('summaryCard');
    const out = document.getElementById('summaryOut');
    card.style.display = 'block';
    out.innerHTML = formatText(text);
  }

  function updateSummaryStatus(ready) {
    const el = document.getElementById('summaryStatus');
    const btn = document.getElementById('genBtn');
    if (ready && activeSummary) {
      el.innerHTML = `<span style="color:var(--success)">✓ Summary ready</span> — <span style="color:var(--text-muted);font-size:0.75rem">${activeSummary.length.toLocaleString()} chars · select scenarios below and generate drafts</span>`;
      el.style.fontStyle = 'normal';
      btn.disabled = false;
    } else {
      el.innerHTML = '⚠️ No summary yet — generate a summary in the left panel first.';
      el.style.fontStyle = 'italic';
      btn.disabled = true;
    }
  }

  // ── Scenario chips ─────────────────────────────────────────────────────────
  function toggleChip(id) {
    const chip = document.getElementById('chip-' + id);
    if (selectedScenarios[id]) {
      delete selectedScenarios[id];
      chip.classList.remove('selected');
    } else {
      selectedScenarios[id] = SCENARIO_DATA[id];
      chip.classList.add('selected');
    }
  }

  // ── Generate scenarios ─────────────────────────────────────────────────────
  async function generateScenarios() {
    if (!activeSummary) { alert('Please generate a policy summary first.'); return; }

    const list = [...Object.values(selectedScenarios)];
    const cName = document.getElementById('customName').value.trim();
    const cDesc = document.getElementById('customDesc').value.trim();
    if (cName && cDesc) {
      list.push({
        name: cName,
        description: cDesc,
        custom_requirements: document.getElementById('customReqs').value.trim()
      });
    }

    if (list.length === 0) {
      alert('Please select at least one scenario chip, or fill in a custom scenario name and description.');
      return;
    }

    showStatus('genStatus', 'loading', `⚡ Generating ${list.length} scenario draft(s) — please wait...`);
    document.getElementById('genBtn').disabled = true;
    document.getElementById('draftsContainer').innerHTML = '';

    let successCount = 0;
    for (const s of list) {
      const el = makePlaceholder(s.name);
      document.getElementById('draftsContainer').appendChild(el);
      try {
        const r = await fetch('/api/generate-scenario', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            summary: activeSummary,
            scenario_name: s.name,
            scenario_description: s.description,
            custom_requirements: s.custom_requirements || ''
          })
        });
        const d = await r.json();
        if (d.error) throw new Error(d.error);
        fillDraft(el, s.name, d.draft);
        successCount++;
      } catch (e) {
        fillError(el, s.name, e.message);
      }
    }

    showStatus('genStatus', 'success', `✓ Generated ${successCount}/${list.length} scenario draft(s) — change selections to iterate`);
    document.getElementById('genBtn').disabled = false;
  }

  // ── Draft rendering helpers ────────────────────────────────────────────────
  function makePlaceholder(name) {
    const d = document.createElement('div');
    d.className = 'draft-card';
    d.innerHTML = `
      <div class="draft-header">
        <span class="draft-title">⏳ Generating: ${escHtml(name)}</span>
        <div class="spinner" style="border-top-color:var(--teal)"></div>
      </div>
      <div class="draft-body" style="color:var(--text-dim);font-style:italic">Drafting adapted policy...</div>`;
    return d;
  }

  function fillDraft(el, name, text) {
    el.innerHTML = `
      <div class="draft-header">
        <span class="draft-title">📜 ${escHtml(name)}</span>
        <button class="copy-btn" onclick="copyDraft(this)">Copy Draft</button>
      </div>
      <div class="draft-body">${formatText(text)}</div>`;
  }

  function fillError(el, name, msg) {
    el.innerHTML = `
      <div class="draft-header">
        <span class="draft-title" style="color:var(--error)">✕ Failed: ${escHtml(name)}</span>
      </div>
      <div class="draft-body" style="color:var(--error)">${escHtml(msg)}</div>`;
  }

  function clearDrafts() {
    document.getElementById('draftsContainer').innerHTML = `
      <div class="empty-state">
        <span class="icon">📜</span>
        <p>Adapted policy drafts will appear here.</p>
        <p style="font-size:.75rem;margin-top:.3rem">Select scenarios above and click <strong>Generate</strong>.</p>
        <p style="font-size:.72rem;margin-top:.5rem;color:var(--text-dim)">You can change scenarios and regenerate at any time.</p>
      </div>`;
    document.getElementById('genStatus').innerHTML = '';
  }

  // ── Text formatter ─────────────────────────────────────────────────────────
  function formatText(t) {
    return t
      .replace(/^# (.+)$/gm, '<h2 style="font-size:1rem;color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
      .replace(/^## (.+)$/gm, '<h2 style="color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
      .replace(/^### (.+)$/gm, '<h3 style="color:var(--teal);font-family:JetBrains Mono,monospace;font-size:.82rem;margin:.4rem 0 .2rem">$1</h3>')
      .replace(/^---+$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:.5rem 0">')
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--green-light)">$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/^[•\-] (.+)$/gm, '<li style="margin-left:1.2rem;margin-bottom:.2rem">$1</li>')
      .replace(/(<li.*<\/li>)/gs, '<ul style="margin:.3rem 0">$1</ul>')
      .replace(/\n/g, '<br>');
  }

  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // ── Utilities ──────────────────────────────────────────────────────────────
  function showStatus(id, type, msg) {
    const spin = type === 'loading' ? '<div class="spinner"></div>' : '';
    document.getElementById(id).innerHTML = `<div class="status ${type}">${spin}${msg}</div>`;
  }

  function copyEl(id) {
    const el = document.getElementById(id);
    navigator.clipboard.writeText(el.innerText || el.value)
      .then(() => alert('Copied to clipboard!'));
  }

  function copyDraft(btn) {
    const body = btn.closest('.draft-card').querySelector('.draft-body');
    navigator.clipboard.writeText(body.innerText)
      .then(() => { btn.textContent = '✓ Copied!'; setTimeout(() => btn.textContent = 'Copy Draft', 2000); });
  }
</script>
</body>
</html>"""

# ─── Groq API helper (100% FREE) ───────────────────────────────────────────────
def call_groq(system_prompt, user_prompt):
    """
    Call the Groq API via direct HTTP — no SDK required.
    Groq uses the OpenAI-compatible chat completions format.

    Free tier: 30 req/min · 14,400 req/day · No credit card needed.
    Model: llama-3.3-70b-versatile — excellent quality, very fast on Groq hardware.

    Raises RuntimeError with a clear, user-friendly message on any failure.
    """
    key = validate_api_key()

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": 3000,
        "temperature": 0.4,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The request timed out after 120 seconds.\n"
            "The policy text may be very long — try trimming it and retrying."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to the Groq API.\n"
            "Please check your internet connection and try again."
        )

    # ── Handle HTTP errors with clear, actionable messages ──────────────────
    if resp.status_code == 401:
        raise RuntimeError(
            "Invalid Groq API key (401 Unauthorised).\n"
            "Please check your key at https://console.groq.com and update it in policy_app.py."
        )

    if resp.status_code == 403:
        raise RuntimeError(
            "Access denied (403 Forbidden).\n"
            "Your Groq API key may have been revoked. "
            "Create a new one at https://console.groq.com → API Keys."
        )

    if resp.status_code == 429:
        # Groq includes a Retry-After header when rate-limited
        retry_after = resp.headers.get("Retry-After", "a few seconds")
        try:
            err_detail = resp.json().get("error", {}).get("message", "")
        except Exception:
            err_detail = ""
        raise RuntimeError(
            f"Groq rate limit reached (429). Please wait {retry_after} and try again.\n"
            f"Free tier allows 30 requests/minute and 14,400/day.\n"
            + (f"Detail: {err_detail}" if err_detail else "")
        )

    if resp.status_code == 503:
        raise RuntimeError(
            "Groq servers are temporarily unavailable (503).\n"
            "This is rare — please wait 15–30 seconds and try again."
        )

    if not resp.ok:
        # Catch any other unexpected HTTP status
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:300])
        except Exception:
            msg = resp.text[:300]
        raise RuntimeError(
            f"Groq API returned HTTP {resp.status_code}: {msg}"
        )

    # ── Parse the successful response ───────────────────────────────────────
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(
            f"Could not parse Groq API response (HTTP {resp.status_code}). Please try again."
        )

    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Groq API error: {err.get('message', str(err))}"
        )

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(
            f"Unexpected response structure from Groq API: {data}"
        )

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        scenarios=PREDEFINED_SCENARIOS,
        default_policy=DEFAULT_POLICY_TEXT
    )

@app.route("/api/extract-pdf", methods=["POST"])
def extract_pdf():
    """
    Extract plain text from an uploaded PDF file.
    Tries pdfplumber → pypdf → PyPDF2 in order.
    Returns a clear error if no PDF library is installed, rather than crashing.
    """
    # Check up front that we have at least one PDF library available
    if _PDF_BACKEND is None:
        return jsonify({
            "error": (
                "No PDF library is installed on this server. "
                "Please run ONE of the following commands in your terminal, then restart the app:\n\n"
                "  pip install pdfplumber       ← recommended\n"
                "  pip install pypdf            ← alternative\n"
                "  pip install PyPDF2           ← older alternative\n\n"
                "Once installed, upload your PDF again."
            )
        }), 500

    if "file" not in request.files:
        return jsonify({"error": "No file was attached to the request."}), 400

    f = request.files["file"]

    if not f.filename:
        return jsonify({"error": "No filename detected — please select a PDF file."}), 400

    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": f'"{f.filename}" is not a PDF. Please upload a .pdf file.'}), 400

    raw_bytes = f.read()
    if len(raw_bytes) == 0:
        return jsonify({"error": "The uploaded file is empty. Please try again with a valid PDF."}), 400

    try:
        text = _extract_text_from_pdf_bytes(raw_bytes)

        if not text or not text.strip():
            return jsonify({
                "error": (
                    "The PDF was opened but no readable text was found. "
                    "This usually means it is a scanned image PDF without OCR. "
                    "Try copying the text manually and using the 'Paste Text' tab instead."
                )
            }), 400

        return jsonify({"text": text.strip(), "chars": len(text.strip()), "backend": _PDF_BACKEND})

    except Exception as e:
        return jsonify({
            "error": (
                f"Could not read this PDF ({type(e).__name__}: {e}). "
                "The file may be password-protected or corrupted. "
                "Try the 'Paste Text' tab as an alternative."
            )
        }), 500


def _extract_text_from_pdf_bytes(raw_bytes):
    """
    Extract all text from PDF bytes using whichever library is available.
    Returns a single string with page text joined by newlines.
    """
    if _PDF_BACKEND == "pdfplumber":
        pages = []
        with _pdfplumber_mod.open(BytesIO(raw_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
        return "\n\n".join(pages)

    elif _PDF_BACKEND == "pypdf":
        pages = []
        reader = _pypdf_mod.PdfReader(BytesIO(raw_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
        return "\n\n".join(pages)

    elif _PDF_BACKEND == "PyPDF2":
        pages = []
        reader = _PyPDF2_mod.PdfReader(BytesIO(raw_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
        return "\n\n".join(pages)

    return ""

@app.route("/api/summarise", methods=["POST"])
def summarise():
    data = request.get_json()
    policy_text = data.get("policy_text", "").strip()
    if not policy_text:
        return jsonify({"error": "No policy text provided"}), 400

    system = (
        "You are a senior environmental and social risk management specialist with expertise in "
        "sustainable banking, IFC Performance Standards, and ESG policy frameworks. You produce clear, "
        "structured, professional summaries of ESRM policies that are accessible to both risk specialists "
        "and credit officers. Focus on practical implications for lending operations, the institution's "
        "E&S risk controls, and the overall regulatory and sustainability posture of the policy."
    )

    prompt = f"""Analyse the following Environmental and Social Risk Management (ESRM) policy document and produce a comprehensive, structured summary.

Your summary MUST clearly cover all three of these required areas:

1. **Main Goals** — What is this ESRM policy trying to achieve? What E&S risk management commitments and sustainability objectives are central?
2. **Key Measures & Strategies** — What specific mechanisms, controls, and screening processes does the policy use to manage E&S risks in lending and internal operations?
3. **Overall Policy Direction** — What does this policy signal about the institution's broader sustainability values, risk appetite, and regulatory posture?

Structure your summary exactly as follows:

## 📋 Policy Overview
[2–3 sentences: what this policy is, who it applies to, and its overall purpose]

## 🎯 Main Goals
[5–7 bullet points covering the primary E&S risk management objectives and sustainability commitments]

## 🔑 Key Measures & Strategies

### 🏦 Lending Risk Management
[3–5 bullet points on E&S screening, risk categorisation, and due diligence requirements for lending]

### 🚫 Exclusions & Restrictions
[3–5 bullet points on banned/illegal activities list and E&S negative list with portfolio thresholds]

### 🌍 Environmental Commitments
[3–5 bullet points on climate risk, biodiversity, resource efficiency, and circular economy measures]

### 👥 Social & Labour Rights
[3–5 bullet points on labour standards, indigenous peoples, gender, health & safety, and community rights]

## 📈 Notable Policies & Practices
[3–5 notable or distinctive aspects of this ESRM policy worth highlighting]

## 🧭 Overall Policy Direction
[2–3 sentences describing the broader strategic posture, sustainability values, and regulatory philosophy signalled by this policy]

---
POLICY TEXT:
{policy_text[:10000]}"""

    try:
        result = call_groq(system, prompt)
        return jsonify({"summary": result})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/generate-scenario", methods=["POST"])
def generate_scenario():
    data = request.get_json()
    summary = data.get("summary", "").strip()
    scenario_name = data.get("scenario_name", "Custom Scenario")
    scenario_description = data.get("scenario_description", "").strip()
    custom_requirements = data.get("custom_requirements", "").strip()

    if not summary:
        return jsonify({"error": "No summary provided. Please generate a summary first."}), 400
    if not scenario_description:
        return jsonify({"error": "No scenario description provided"}), 400

    system = (
        "You are a senior environmental and social risk management consultant with expertise in "
        "sustainable banking, IFC Performance Standards, ESRM frameworks, and sector-specific E&S risk "
        "assessment. You create adapted ESRM policy frameworks that are professional, context-specific, "
        "and actionable. Each adapted framework must clearly reflect its target sector's risks and "
        "constraints, differ meaningfully from other adaptations in emphasis and approach, cite relevant "
        "standards and regulations where applicable, and maintain a formal, policy-appropriate tone throughout."
    )

    prompt = f"""Using the ESRM policy summary below as your foundation, generate a comprehensive ADAPTED ESRM POLICY FRAMEWORK for the following scenario.

SCENARIO: {scenario_name}
CONTEXT & PRIORITIES: {scenario_description}
{f'ADDITIONAL REQUIREMENTS: {custom_requirements}' if custom_requirements else ''}

ORIGINAL ESRM POLICY SUMMARY:
{summary[:5000]}

INSTRUCTIONS:
- The adapted framework must clearly reflect the scenario's sector risks, regulatory context, and operational constraints.
- It must differ meaningfully from the original policy in focus, tone, and recommended provisions.
- Cite relevant standards or regulations where applicable (e.g. IFC Performance Standards, ILO Conventions, CBSL Directions, Bangladesh Bank Guidelines).
- Maintain formal, policy-style language throughout.
- Structure as follows:

---
# ADAPTED ESRM POLICY FRAMEWORK
## Scenario: {scenario_name}
### Derived from: Commercial Bank of Ceylon PLC — Group ESRM Policy v3.0 (January 2025)
---

## 1. PURPOSE & SCOPE
[Adapted purpose and scope for this specific sector/scenario, including which activities, geographies, and borrower types are covered]

## 2. CORE E&S RISK MANAGEMENT GOALS FOR THIS CONTEXT
[4–6 goals specifically relevant to this scenario — not a copy of the original]

## 3. E&S SCREENING & RISK CATEGORISATION
[How projects/borrowers in this sector should be screened; risk categories (High/Medium/Low or A/B/C) and categorisation criteria]

## 4. KEY ENVIRONMENTAL RISKS & MITIGATION MEASURES
[Sector-specific environmental risks and required mitigation strategies, applying the avoidance → minimisation → remediation hierarchy]

## 5. KEY SOCIAL & LABOUR RISKS & MITIGATION MEASURES
[Sector-specific social risks — labour rights, community impacts, gender, indigenous peoples, health & safety — and required actions]

## 6. EXCLUSIONS & RESTRICTIONS SPECIFIC TO THIS SCENARIO
[Any additional activities to exclude or restrict beyond the standard Banned/Negative List, given this sector's profile]

## 7. BORROWER OBLIGATIONS & LOAN COVENANTS
[What the borrower must commit to — ESMPs, audits, reporting, certifications — and how these are enforced via loan agreements]

## 8. MONITORING & COMPLIANCE REQUIREMENTS
[How the Bank should monitor E&S performance during the loan tenure — site visits, reporting frequency, trigger events for review]

## 9. SCENARIO-SPECIFIC RECOMMENDATIONS
[3–5 specific, actionable recommendations unique to this scenario that would not appear in another adaptation]

---
*This adapted framework reflects the E&S risk profile and regulatory context of the "{scenario_name}" scenario and may differ substantially from the original ESRM policy in emphasis, scope, and recommended provisions.*"""

    try:
        result = call_groq(system, prompt)
        return jsonify({"draft": result, "scenario": scenario_name})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

# ─── Startup ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 62)
    print("  PolicyAI — ESRM Policy Summariser & Scenario Generator")
    print("  Pre-loaded: CBC Group ESRM Policy v3.0 (January 2025)")
    print(f"  Powered by Groq AI — Model: {GROQ_MODEL}")
    print("  Free tier: 30 req/min · 14,400 req/day · No card needed")
    print("=" * 62)

    key = GROQ_API_KEY.strip()
    if not key or key == "PASTE_YOUR_GROQ_KEY_HERE":
        print("\n⚠️  WARNING: No Groq API key found!")
        print("   1. Go to https://console.groq.com  (free signup)")
        print("   2. Click API Keys → Create API Key")
        print("   3. Paste the key (gsk_...) into policy_app.py")
        print("      where it says PASTE_YOUR_GROQ_KEY_HERE\n")
    else:
        masked = key[:8] + "..." + key[-4:]
        print(f"\n✓ Groq API Key loaded ({masked})")

    if _PDF_BACKEND:
        print(f"✓ PDF backend: {_PDF_BACKEND} (PDF upload is enabled)")
    else:
        print("⚠️  No PDF library — PDF upload will prompt to install one.")
        print("   Run:  pip install pdfplumber")

    print("\n  Open in browser: http://localhost:5000")
    print("=" * 62 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)