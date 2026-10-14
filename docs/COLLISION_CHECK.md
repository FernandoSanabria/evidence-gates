# Collision check — evidence-gates (Stage 0.1)

- Run: 2026-10-14T07:25:48Z, before any scaffold file other than this one existed.
- Names checked: `evidence-gates`, `evidence_gates`, `prereg`. On npm and PyPI the near variants `evidence-gate` and `evidencegates` are listed too.
- Each block is a command exactly as run (through `/bin/sh -c`) followed by its raw output. `cut -c1-240` and `cut -c1-200` only shorten long description lines. Third-party e-mail addresses that the registries return are replaced by `<email redacted>`.
- Rule under test (from the brief): if `evidence-gates` is taken as a repo under a plausible owner, stop and report; do not pick a new name alone.

## 1. GitHub repositories

**Tool version**

```console
$ gh --version | head -1
gh version 2.102.0 (2026-09-30)
```

**The exact target repo. HTTP 404 means the URL is free**

```console
$ gh api -i repos/FernandoSanabria/evidence-gates 2>&1 | head -1
HTTP/2.0 404 Not Found
```

**Repo-NAME match for each name (owner/repo, stars, last update, description)**

```console
$ for n in evidence-gates evidence_gates prereg; do echo "== name match: $n"; gh search repos "$n" --match name --limit 30 --json fullName,description,stargazersCount,updatedAt --jq '.[] | [.fullName, (.stargazersCount|tostring), .updatedAt, (.description // "")] | @tsv' | cut -c1-240; done
== name match: evidence-gates
m-sanchez/evidence-gates	0	2026-09-01T19:49:01Z	Merged into @m-sanchez/grounded-claims - archived, history intact
MARCCHERGGI/evidence-gates	0	2026-08-18T22:10:35Z	A self-improving agent cannot grade its own homework. Ladder gates that open only on external evidence, fail closed on outage, and allow real demotion.
ksungz/ax-evidence-gates	0	2026-07-27T00:21:57Z	공개 근거와 합성 데이터로 AI 결과물을 점검하는 AX 품질 게이트 3종
== name match: evidence_gates
MARCCHERGGI/evidence-gates	0	2026-08-18T22:10:35Z	A self-improving agent cannot grade its own homework. Ladder gates that open only on external evidence, fail closed on outage, and allow real demotion.
m-sanchez/evidence-gates	0	2026-09-01T19:49:01Z	Merged into @m-sanchez/grounded-claims - archived, history intact
ksungz/ax-evidence-gates	0	2026-07-27T00:21:57Z	공개 근거와 합성 데이터로 AI 결과물을 점검하는 AX 품질 게이트 3종
== name match: prereg
crsh/prereg	54	2026-09-10T12:22:21Z	Collection of R Markdown templates to create preregistration documents
turnermm/preregister	2	2022-01-25T04:08:26Z	Dokuwiki plugin for registering by means of a confirmation link, with built-in captcha 
aaronpeikert/bayes-prereg	6	2026-10-05T14:47:35Z	
bsiepe/ADEMP-PreReg	31	2026-09-12T06:11:03Z	ADEMP preregistration protocol for simulation studies
jessicaflannery/fmri-prereg	4	2025-06-11T15:46:20Z	A second option to work with fMRI prereg
dheeraj-rn/preregistration	5	2025-07-31T17:00:17Z	An app to simplify registation of elective subjects for students
JehhB/DICT-prereg	0	2024-08-09T03:52:09Z	
ml-preregister/preregistration-template	3	2024-05-24T15:02:21Z	Preregistration template for predictive modeling. A quick starter kit for new ML projects. Fork this repo to get started.
j-5chneider/preregRS	6	2026-10-07T11:40:22Z	
NotLafuan/prereg	0	2025-12-18T08:30:12Z	This repository has the code for auto-adding course and stuff on https://prereg1.iium.edu.my/.
xzp1995/PreReg	0	2017-10-14T03:32:24Z	Prefix L1, L2 and Linf Regression with 1D and 2D vector input
xycloops123/PreReg	1	2014-10-26T16:25:24Z	Developed session tracking system using various technologies like Java, JSP, MySQL, HTML5, JavaScript.
JuliusChristian/prereg	0	2022-06-02T03:09:24Z	
xzhipeng/PreReg	0	2017-10-14T03:08:58Z	Prefix L1, L2 and Linf Regression with 1D and 2D vector input
Savi-Swar/prereg	0	2026-09-02T15:48:44Z	
Ale-ara/prereg	0	2024-04-20T20:33:25Z	
smunagala/prereg	0	2022-12-17T00:58:12Z	
mzhn-fsp-dnr/prereg	0	2024-10-20T12:41:08Z	Модуль для обработки предварительного бронирования
UdyrPerson/prereg	0	2026-10-11T23:39:34Z	Empreintes de pre-enregistrement (SHA-256)
LLuettgau/prereg	0	2023-01-18T10:40:53Z	
swamphacks/2017-Preregistration	2	2018-01-18T21:04:34Z	Static content for SwampHacks
areong/MillionLiveTheaterDaysPreregistrationTool	4	2019-06-14T06:48:55Z	ミリオンライブ！ シアターデイズ 事前登録自動ツールです！
Arnaldo-Isac-Manguene/prereg	0	2024-01-11T13:15:09Z	
mnikoobayan/prereg	0	2024-03-14T21:53:34Z	Pre-registration system for Qom University students
echivambo/prereg	1	2017-10-19T19:24:07Z	Sistema de gestäo de candidatura
prereg/prereg	1	2023-04-26T09:11:47Z	
szekely-zsuzsa/prereg	0	2024-10-20T12:22:27Z	
DEAFONE-exe/PreReg	0	2025-07-01T06:50:22Z	
Bornoz/prereg	0	2026-10-13T21:08:21Z	Pre-registered, signed, falsifiable claims on technocore.chat, with the verifier that recomputes the score without trusting the agent.
cran/prereg	0	2022-01-21T03:33:18Z	:exclamation: This is a read-only mirror of the CRAN R package repository.  prereg — R Markdown Templates to Preregister Scientific Studies. Homepage: https://github.com/crsh/prereg  Report bugs for this p
```

**Repos whose name is exactly evidence-gates or evidence_gates, any owner**

```console
$ for n in evidence-gates evidence_gates; do gh search repos "$n" --match name --limit 100 --json fullName --jq '.[] | select(.fullName|test("/evidence[-_]gates$";"i")) | .fullName'; done | sort -u
MARCCHERGGI/evidence-gates
m-sanchez/evidence-gates
```

**The exact-name repos in detail**

```console
$ for r in MARCCHERGGI/evidence-gates m-sanchez/evidence-gates; do gh repo view "$r" --json nameWithOwner,description,isArchived,createdAt,pushedAt,stargazerCount,licenseInfo --jq '"\(.nameWithOwner) | archived=\(.isArchived) | created=\(.createdAt) | pushed=\(.pushedAt) | stars=\(.stargazerCount) | license=\(.licenseInfo.key // "none") | \(.description)"'; done
MARCCHERGGI/evidence-gates | archived=false | created=2026-08-18T22:10:17Z | pushed=2026-08-18T22:10:19Z | stars=0 | license=mit | A self-improving agent cannot grade its own homework. Ladder gates that open only on external evidence, fail closed on outage, and allow real demotion.
m-sanchez/evidence-gates | archived=true | created=2026-08-31T18:30:29Z | pushed=2026-09-01T19:48:14Z | stars=0 | license=mit | Merged into @m-sanchez/grounded-claims - archived, history intact
```

**Does either carry a Claude Code plugin manifest? (HTTP 404 means no .claude-plugin directory)**

```console
$ for r in MARCCHERGGI/evidence-gates m-sanchez/evidence-gates; do printf '%s: ' "$r"; gh api -i "repos/$r/contents/.claude-plugin" 2>&1 | head -1; done
MARCCHERGGI/evidence-gates: HTTP/2.0 404 Not Found
m-sanchez/evidence-gates: HTTP/2.0 404 Not Found
```

**Any-field match (name, description, readme), first 12 for each name**

```console
$ for n in evidence-gates evidence_gates prereg; do echo "== any field: $n"; gh search repos "$n" --limit 12 --json fullName,stargazersCount,updatedAt,description --jq '.[] | [.fullName, (.stargazersCount|tostring), .updatedAt, (.description // "")] | @tsv' | cut -c1-200; done
== any field: evidence-gates
beefiker/superloopy	112	2026-10-14T06:30:06Z	Lightweight Codex/Claude loop harness with strict evidence gates.
ValerianXXX/JobFlow	197	2026-10-13T18:06:42Z	Local-first, AI-centered, evidence-gated job application workflow
DY-2026/GameDesignOS	417	2026-10-13T10:16:57Z	Local-first game design OS for AI agents: turn sessions into evidence, experiments, reviewable decisions, and durable project memory—Human Gates and rollb
timtoole02/Camelid	217	2026-10-12T10:18:56Z	Camelid: a Rust-native local inference backend with evidence-gated model compatibility.
Tommy-yw/RunbookHermes	507	2026-10-13T15:01:39Z	Hermes-native AIOps agent for evidence-driven incident response, approval-gated remediation, and runbook learning.
rmbell09-lang/tradesight	168	2026-10-09T09:29:58Z	Self-hosted Python strategy research and Alpaca paper trading with broker reconciliation, evidence gates, and live execution disabled.
AnttiHero/lavern	311	2026-10-08T06:03:56Z	An agentic law firm. Yours. 67 specialist AI agents that review documents through evidence-backed debate, with mandatory human gates and a 10-pass verificatio
Cranot/roam-code	517	2026-10-14T04:16:46Z	Local codebase intelligence CLI + MCP server for AI coding agents: SQLite code graph, 28 languages, 287 commands, 246 MCP tools, change-safety gates, audit ev
VinUni-AI20k/Day22-Responsible-AI-Production-Lab	1	2026-08-29T06:43:10Z	Day 22 PM/PO lab: Responsible AI in Production with evidence, harm mapping, backlog controls and release gates.
pavel-molyanov/molyanov-ai-dev	297	2026-10-08T18:35:14Z	Intent-driven AI-First development methodology for Claude Code and Codex — Project Knowledge, user-spec planning, focused execution, and evidenc
william-ricchiuti/OpenCode-goal-plugin	276	2026-10-14T06:15:01Z	Durable, guarded goal workflows for OpenCode with persistence, safety limits, agent tools, and evidence-gated completion.
anombyte93/prd-taskmaster	607	2026-10-10T12:03:29Z	Zero-config goal-to-tasks engine for Claude Code (the Atlas engine). Graded PRD validation, dependency-ordered task graph, evidence-gated execution.
== any field: evidence_gates
beefiker/superloopy	112	2026-10-14T06:30:06Z	Lightweight Codex/Claude loop harness with strict evidence gates.
DY-2026/GameDesignOS	417	2026-10-13T10:16:57Z	Local-first game design OS for AI agents: turn sessions into evidence, experiments, reviewable decisions, and durable project memory—Human Gates and rollb
rmbell09-lang/tradesight	168	2026-10-09T09:29:58Z	Self-hosted Python strategy research and Alpaca paper trading with broker reconciliation, evidence gates, and live execution disabled.
AnttiHero/lavern	311	2026-10-08T06:03:56Z	An agentic law firm. Yours. 67 specialist AI agents that review documents through evidence-backed debate, with mandatory human gates and a 10-pass verificatio
VinUni-AI20k/Day22-Responsible-AI-Production-Lab	1	2026-08-29T06:43:10Z	Day 22 PM/PO lab: Responsible AI in Production with evidence, harm mapping, backlog controls and release gates.
Cranot/roam-code	517	2026-10-14T04:16:46Z	Local codebase intelligence CLI + MCP server for AI coding agents: SQLite code graph, 28 languages, 287 commands, 246 MCP tools, change-safety gates, audit ev
callhong/bottleneck-scout-v3	35	2026-09-22T03:45:04Z	Chinese-first bottleneck investment research skill with evidence gates and PDF reports
victorzhang016-code/victor-design	69	2026-10-05T16:45:03Z	Evidence-led design skill for AI agents: subject-first art direction, form sanity gates, density craft model, and three release gates for post
cachenetics/170tune	85	2026-10-13T16:43:23Z	Tuning and qualification harness for the NVIDIA CMP 170HX (GA100). Measures, gates and recovers clock/voltage settings, and treats a completed benchmark as 
DevOpsAIguru123/awesome-agentic-devops	82	2026-10-08T11:28:25Z	Curated + scored map of official MCP servers and agents for DevOps, Cloud, SRE, and Platform Engineering — every entry rated on productio
Minh-Tam-Solution/SDLC-Enterprise-Framework	20	2026-10-09T06:07:49Z	AI+Human software delivery methodology with risk-tiered governance, executable gates, an evidence-based lifecycle and tool-agnostic 
forthfate/openorbit	5	2026-09-27T12:51:06Z	Open control plane for recurring AI automations: runners, workflows, evidence, supervision, and approval gates.
== any field: prereg
crsh/prereg	54	2026-09-10T12:22:21Z	Collection of R Markdown templates to create preregistration documents
turnermm/preregister	2	2022-01-25T04:08:26Z	Dokuwiki plugin for registering by means of a confirmation link, with built-in captcha 
aaronpeikert/bayes-prereg	6	2026-10-05T14:47:35Z	
jessicaflannery/fmri-prereg	4	2025-06-11T15:46:20Z	A second option to work with fMRI prereg
bsiepe/ADEMP-PreReg	31	2026-09-12T06:11:03Z	ADEMP preregistration protocol for simulation studies
dheeraj-rn/preregistration	5	2025-07-31T17:00:17Z	An app to simplify registation of elective subjects for students
JehhB/DICT-prereg	0	2024-08-09T03:52:09Z	
ml-preregister/preregistration-template	3	2024-05-24T15:02:21Z	Preregistration template for predictive modeling. A quick starter kit for new ML projects. Fork this repo to get started.
j-5chneider/preregRS	6	2026-10-07T11:40:22Z	
swamphacks/2017-Preregistration	2	2018-01-18T21:04:34Z	Static content for SwampHacks
areong/MillionLiveTheaterDaysPreregistrationTool	4	2019-06-14T06:48:55Z	ミリオンライブ！ シアターデイズ 事前登録自動ツールです！
ApisXia/PartialMedPreregistration	2	2022-11-04T04:47:11Z	
```

## 2. npm and PyPI

**Registry status per name (200 = taken, 404 = free). PyPI treats - and _ as the same name**

```console
$ for n in evidence-gates evidence_gates prereg evidence-gate evidencegates; do printf 'npm  %-16s HTTP %s\n' "$n" "$(curl -s -o /dev/null -w '%{http_code}' "https://registry.npmjs.org/$n")"; done; for n in evidence-gates evidence_gates prereg evidence-gate evidencegates; do printf 'pypi %-16s HTTP %s\n' "$n" "$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/$n/json")"; done
npm  evidence-gates   HTTP 404
npm  evidence_gates   HTTP 404
npm  prereg           HTTP 404
npm  evidence-gate    HTTP 200
npm  evidencegates    HTTP 404
pypi evidence-gates   HTTP 404
pypi evidence_gates   HTTP 404
pypi prereg           HTTP 200
pypi evidence-gate    HTTP 200
pypi evidencegates    HTTP 404
```

**Who holds the names that are taken**

```console
$ for n in evidence-gates evidence_gates prereg evidence-gate evidencegates; do c=$(curl -s -o /dev/null -w '%{http_code}' "https://registry.npmjs.org/$n"); [ "$c" = 200 ] && curl -s "https://registry.npmjs.org/$n/latest" | jq -r '"npm \(.name) \(.version) | \(.description) | author: \((if (.author|type)=="object" then .author.name else .author end) // "-")"'; done; for n in evidence-gates evidence_gates prereg evidence-gate evidencegates; do c=$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/$n/json"); [ "$c" = 200 ] && curl -s "https://pypi.org/pypi/$n/json" | jq -r '.info | "pypi \(.name) \(.version) | \(.summary) | author: \(.author // .author_email // "-")"'; done; true
npm evidence-gate 1.0.1 | Stop your AI from making up facts about your own data. A pre-generation gate that decides whether an LLM may summarize, based on evidence coverage, freshness, and quality. | author: LopezDray
pypi prereg 0.5.6 | Preregister your plan to prevent p-hacking and unfalsifiable post-hoc analysis | author: Elliot Tower <email redacted>
pypi evidence-gate 0.1.0 | Catches green CI verdicts whose audit trail is missing, late, or unclear. | author: Nick Cunningham <email redacted>
```

**npm search API, first 10 results per text**

```console
$ for q in evidence-gates evidence_gates prereg; do echo "== npm search text=$q"; curl -s "https://registry.npmjs.org/-/v1/search?text=$q&size=10" | jq -r '"total: \(.total)", (.objects[] | "  \(.package.name) \(.package.version) | \((.package.description // "")[0:90])")'; done
== npm search text=evidence-gates
total: 19440
  @jterrats/open-orchestra 1.3.1 | Local control plane for AI-assisted development orchestration, evidence gates, and agent w
  psyclaw 0.30.17 | A standalone, evidence-grounded social-science research agent with research contracts, evi
  @kanipre/changeproof 0.1.3 | Declarative evidence gates for pull requests.
  @kingizie/build-standard 4.0.2 | Izie's professional build system: a hardened constitution, ordered lifecycle, semantic ski
  akela 0.1.4 | A deterministic context compiler for AI agents — evidence-driven context engineering besid
  @fabioeloi/whw 0.2.1 | WHW (Why · How · What) — portable, resumable and verifiable work for humans and coding age
  @zhushanwen/coding-workflow 2.4.0 | CI for AI coding agents: event-sourced ledger, evidence gates, and a deterministic runner 
  riqor 0.2.6 | 100 specialist Skills, evidence gates, and session continuity for AI-assisted engineering
  @mmerterden/multi-agent-pipeline 20.24.0 | 6-phase AI development pipeline with full orchestration on Claude Code, Copilot CLI and Co
  aero-agent-roles 1.2.3 | The role layer for aerospace engineering agents: professional roles that bind verified Aer
== npm search text=evidence_gates
total: 0
== npm search text=prereg
total: 2
  @tasks-md/lint 0.10.2 | Validate TASKS.md files against the spec
  node-addu-sis 1.9.0 | A node.js API for accessing AdDU SIS data.
```

## 3. Claude Code plugin marketplaces

**Plugin names in Anthropic's three marketplaces: exact hits and names containing evidence/prereg**

```console
$ for r in anthropics/claude-plugins-official anthropics/claude-plugins-community anthropics/claude-code; do printf '%s: ' "$r"; curl -sL "https://raw.githubusercontent.com/$r/main/.claude-plugin/marketplace.json" | jq -r '"\(.name), \(.plugins|length) plugins | exact-name hits: \([.plugins[].name | select(. == "evidence-gates" or . == "evidence_gates" or . == "prereg")] | tostring) | names containing evidence/prereg: \([.plugins[].name | select(test("evidence|prereg";"i"))] | tostring)"'; done
anthropics/claude-plugins-official: claude-plugins-official, 315 plugins | exact-name hits: [] | names containing evidence/prereg: []
anthropics/claude-plugins-community: claude-community, 2283 plugins | exact-name hits: [] | names containing evidence/prereg: []
anthropics/claude-code: claude-code-plugins, 13 plugins | exact-name hits: [] | names containing evidence/prereg: []
```

**Third-party marketplace.json / plugin.json files that mention each name (GitHub code search, first 10)**

```console
$ for n in evidence-gates evidence_gates prereg; do for f in marketplace.json plugin.json; do echo "== $n in $f"; gh search code "$n" --filename "$f" --limit 10 --json repository,path --jq '.[] | [.repository.nameWithOwner, .path] | @tsv'; sleep 7; done; done
== evidence-gates in marketplace.json
beefiker/superloopy	.claude-plugin/marketplace.json
caseyrtalbot/forge	.claude-plugin/marketplace.json
== evidence-gates in plugin.json
hashgraph-online/awesome-codex-plugins	plugins/beefiker/superloopy/.codex-plugin/plugin.json
beefiker/superloopy	plugin.json
beefiker/superloopy	.codex-plugin/plugin.json
beefiker/superloopy	.gemini-plugin/plugin.json
beefiker/superloopy	.claude-plugin/plugin.json
caseyrtalbot/forge	.claude-plugin/plugin.json
lhy0718/AutoLabOS	plugins/autolabos-research-governor/.codex-plugin/plugin.json
== evidence_gates in marketplace.json
== evidence_gates in plugin.json
== prereg in marketplace.json
atomicstrata/epistemic	.claude-plugin/marketplace.json
brycewang-stanford/Auto-Empirical-Research-Skills	skills/50-brycewang-aer-skills/.claude-plugin/marketplace.json
elliottower/reproducible-science	.claude-plugin/marketplace.json
GuoCheng24/groundwork	.claude-plugin/marketplace.json
hashgraph-online/awesome-codex-plugins	.agents/plugins/marketplace.json
brycewang-stanford/Awesome-Journal-Skills	Review-of-Educational-Research-Skills/.claude-plugin/marketplace.json
brycewang-stanford/Awesome-Journal-Skills	.claude-plugin/marketplace.json
brycewang-stanford/AER-Skills	.claude-plugin/marketplace.json
AlterLab-IEU/AlterLab-Academic-Skills	.claude-plugin/marketplace.json
iskendersancar/claude-research-skills	.claude-plugin/marketplace.json
== prereg in plugin.json
elliottower/reproducible-science	packages/prereg/plugin/.claude-plugin/plugin.json
mattermost/mattermost-plugin-gitlab	plugin.json
mattermost/mattermost-plugin-github	plugin.json
phdemotions/research-methods	.claude/hooks-plugin.json
brycewang-stanford/Awesome-Journal-Skills	Psychological-Science-Skills/.claude-plugin/plugin.json
brycewang-stanford/Awesome-Journal-Skills	Psychological-Bulletin-Skills/.claude-plugin/plugin.json
elliottower/reproducible-science	packages/repro/plugin/.claude-plugin/plugin.json
brycewang-stanford/Awesome-Journal-Skills	Developmental-Psychology-Skills/.claude-plugin/plugin.json
brycewang-stanford/Awesome-Journal-Skills	Journal-of-Applied-Psychology-Skills/.claude-plugin/plugin.json
K-Dense-AI/scientific-agents	scientific-agents/psycholinguist/plugin.json
```

**The plugin named prereg that the search surfaced**

```console
$ gh api repos/elliottower/reproducible-science/contents/packages/prereg/plugin/.claude-plugin/plugin.json --jq .content | base64 -d | jq -c '{name,version,description,license,repository}'
{"name":"prereg","version":"0.5.6","description":"Freeze a plan before you run it, and record what changed after","license":"MIT","repository":"https://github.com/elliottower/reproducible-science/tree/main/packages/prereg"}
```

## 4. Reading

| Question | Answer |
|---|---|
| Is `FernandoSanabria/evidence-gates` free? | Yes. HTTP 404. |
| Is `evidence-gates` a repo name under another owner? | Yes, twice. `MARCCHERGGI/evidence-gates`: live, MIT, 0 stars, JavaScript (`ladder.mjs`), a design essay on gates that open only on external evidence, one push on 2026-08-18. `m-sanchez/evidence-gates`: archived 2026-09-01, 0 stars, merged into `@m-sanchez/grounded-claims`. Neither has a `.claude-plugin` directory. |
| npm | `evidence-gates`, `evidence_gates` and `prereg` are free. The near variant `evidence-gate` is taken. |
| PyPI | `evidence-gates` and `evidence_gates` are free. `prereg` is taken (0.5.6, a pre-registration tool). The near variant `evidence-gate` is taken. |
| Anthropic's marketplaces | No plugin named `evidence-gates`, `evidence_gates` or `prereg` in the official (315 plugins), community (2,283) or demo (13) marketplace. |
| Third-party marketplaces | A plugin named `prereg` exists in `elliottower/reproducible-science` (0.5.6, MIT, same author as the PyPI package). `evidence-gates` appears only as a keyword or tag in `caseyrtalbot/forge` and `beefiker/superloopy`. |

What follows from it:

- The rule fired: the name is taken as a repo name under two plausible owners, so the work stopped and the owner was asked.
- Nothing technical collides. The install id is `evidence-gates@evidence-gates`, and every command is namespaced (`/evidence-gates:prereg`), so it cannot shadow the `prereg` plugin.
- The README credits the genuinely related pre-registration plugins (`elliottower/reproducible-science`, `reinthal/preregister`, `K-Dense-AI/science-superpowers`) when it is written at Stage 1. It does not credit the `MARCCHERGGI/evidence-gates` essay.

## Owner decision

**2026-10-14: KEEP `evidence-gates`.** Given in answer to the Stage 0.1 stop, after the facts above were put in front of the owner.
