# Method and research boundaries

## Research question

Which institutional support functions are explicitly documented in a small set of official Jamaican sports and education sources relevant to school athletics and higher-level competition?

The question concerns **documented functions**. It does not ask whether a particular programme caused athletic success, how many athletes used it, or whether every athlete can access it. The unit of analysis is the institution. Each institution is counted once for every supported function assigned to it.

## Corpus and selection

Eight institutions were selected purposively to include school competition, tertiary education, athletics administration, and cross-sport support. The selection comprises ISSA, JAAA, UTech, UWI Mona, G C Foster College, JADCO, SDF, and JOA. Private clubs, individual schools, commercial sponsors, overseas collegiate systems, families, and informal support networks are outside this bounded corpus.

Eleven public pages were retrieved from the institutions' official websites on 20 November 2026. A federation event record supplements ISSA's own competition directory. Official institutional pages are primary evidence of what organisations state about their roles; they are not independent evidence of service quality. Search results were used to locate pages, and relevant content was opened and inspected before coding.

The [source register](sources/source-register.md) records exact URLs, the access date, identifiable publication dates, evidence locations, and limits. An access date is not a publication date or proof that a programme currently accepts participants. No full copyrighted page copies or personal athlete records are stored.

## Coding framework

| Function | Inclusion rule |
| --- | --- |
| Competition access or delivery | Explicit competition organisation or an athlete programme that provides competition participation |
| Athlete training | Explicit athlete training or an athletics development and training programme |
| Coach or official education | Explicit coaching or athletics-official education, certification, or development |
| Facilities or infrastructure support | Explicit provision of athletics facilities or financing of sports infrastructure |
| Financial support | Explicit funding of athletes, sports organisations, or programmes, including scholarships |
| Governance or representation | A national athletics governing body or national Olympic committee role |
| Health or welfare support | Explicit athlete well-being services, sports medicine, or an athlete welfare fund |
| Clean sport education or testing | Explicit anti-doping education or testing |

The machine-readable [codebook](data/codebook.json) carries the same definitions. Categories overlap intentionally. For example, a university's competition programme and sports medicine provision produce separate assignments. Financial support for training is not automatically coded as direct athlete training.

Each assignment requires a specific observation and at least one registered source ID. The [input dataset](data/institutions.json) preserves those decisions. No role is inferred solely from an institution's name or general reputation. A missing code means that the function was not established in the selected pages; it does not establish that the function is absent in practice.

## Analysis

For each function, the Python script counts distinct institutions carrying that code. The reported percentage is the function count divided by eight sampled institutions. Because assignments overlap, the percentages need not total 100%. Institution-type counts use one type per entity and therefore do total eight.

The chart and tables report presence of documented functions. A higher number is not a quality score, funding share, indicator of athlete demand, or estimate of national coverage. No weighting, forecasting, causal modelling, or statistical significance testing is appropriate for this purposive descriptive sample.

## Quality checks and reproducibility

The script rejects duplicate institution IDs, duplicate institution-function assignments, unrecognised codes, empty evidence notes, and missing source references. It validates publisher domains and ISO dates. Generated tables and the SVG are deterministic products of the JSON inputs. The `--check` option compares saved outputs with fresh in-memory results.

These checks prevent common data assembly errors. They cannot validate claims made by the organisations or remove coding judgement. This is an AI-assisted, single-workflow coding exercise; there was no independent second coder or inter-rater reliability assessment.

## Material limitations

Official websites differ in detail and freshness. The UWI page retains a COVID-era notice; its descriptions are recorded without assuming current service availability. The JOA scholarship announcement and SDF remit are cross-sport evidence, not track-and-field-specific award records. An ISSA event listing establishes an organiser, not an athlete development effect.

No athlete-level longitudinal dataset was collected. The analysis therefore cannot measure progression, dropout, access inequalities, cost barriers, or the effectiveness of handoffs between institutions. It also cannot identify undocumented partnerships. Any later work on those questions would require additional evidence and an appropriate data collection design.

## Relationship to earlier research

The only original-project background carried forward is Ziana Bennett's USOAR research assistant role with Professor Kisha Lashley on Jamaica's track and field ecosystem. This new extension is self-contained. It makes no claims about earlier research methods, empirical findings, or supervisor approval.
