# Independent EMP research website

Prepared for Hadj Abdelkader Benzater, GitHub account `LhadjBENZATER`.

This copy has its own hosting and weekly update workflow. It does **not** call ChatGPT, OpenAI, Copilot or another AI service. After deployment it runs in GitHub, independently of any ChatGPT subscription or conversation. It needs no OpenAI API key and no Python package installation.

## What updates automatically

| Data | Source and behaviour |
| --- | --- |
| New journal/conference/chapter publications | Public ORCID DOI records, checked against Crossref publisher metadata and author identity. Duplicate DOI records are not added. |
| Crossref citation counts | Refreshed for existing Crossref-registered publications. Displayed separately from Google Scholar counts. |
| Dates and source status | The time and outcome of each automated source check are recorded. Failed sources retain the previous data. |
| Existing repository/poster records | Preserved. Zenodo concept/version DOIs are not added as duplicate works or queried as Crossref records. New repository-only works can be added by editing the catalogue. |
| Google Scholar citation counts, h-index and i10-index | Preserved as dated snapshots. Automatic Scholar scraping is not included. |
| Web of Science review totals | Preserved as dated snapshots. An official Researcher API integration would require separately licensed access and is not configured. |

**A weekly check does not make inaccessible Scholar or WoS values live.** No counts are inferred from another database. The current Scholar snapshot is 68 citations, h-index 5, i10-index 2; the supplied WoS snapshot is 76 review records for 43 manuscripts.

## One-time setup on GitHub Free

Publishing a GitHub Pages site on GitHub Free requires a **public repository**. The website, its code and the included professional/publication data will be public. Confidential manuscript titles, review contents and credentials are not included.

1. Create a new public repository named **`LhadjBENZATER.github.io`** in your `LhadjBENZATER` account. Do not overwrite an existing repository.
2. Extract this archive and upload its **contents**, including the `.github` directory, to the repository's `main` branch. Upload the files, not the ZIP itself.
3. In the repository, open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. If necessary, enable GitHub Actions. The workflow requests repository write permission to store the refreshed public data and Pages permission to deploy it. No personal access token is needed.
5. Open **Actions → Refresh research site and publish → Run workflow**. Wait for a successful run. Verify that both the publication library and the source dates appear correctly.
6. The intended website address is **`https://LhadjBENZATER.github.io/`**. This address is configured in the files but is not proof that the site is already published.

The supplied default schedule is **Sunday at approximately 08:17 Algeria time** (`07:17 UTC`). GitHub may delay scheduled jobs. Change the cron expression in `.github/workflows/weekly-site.yml` to select another time.

The existing ChatGPT-hosted site is not changed by extracting or uploading this copy. Its URL will not automatically become the GitHub address; share the new address after verifying deployment.

## Updating Scholar/WoS figures without ChatGPT

Use GitHub's file editor to edit `metrics-overrides.json`, then commit. The build applies it automatically. For example:

```json
{
  "scholar": {
    "asOf": "2026-11-21",
    "citations": 68,
    "hIndex": 5,
    "i10Index": 2,
    "profileEntries": 28
  },
  "peerReview": {
    "asOf": "2026-11-21",
    "records": 76,
    "manuscripts": 43
  },
  "publicationCitations": {
    "10.1002/ett.70000": 17
  }
}
```

Only enter values verified in the named source. Use the date of the source snapshot. To change the journal list, add `peerReview.journals` as a list of `{ "name": "Journal name", "manuscripts": 1 }` objects; its manuscript total must match the overall total. Replacing the overrides later is fine; omit fields that do not need changing.

For future licensed/custom data sources, keep credentials in GitHub repository secrets; do not put them in JSON files. The provided updater deliberately has no speculative or untested WoS endpoint adapter.

## Local use and editing

Python 3.10+ is sufficient:

```text
python refresh.py --apply
python generate.py
python -m unittest discover -s tests -v
python verify.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/` for local preview. `python refresh.py` without `--apply` checks sources without writing changes.

- `index.template.html`: editable biography and page structure.
- `dist/publications.json`: publication catalogue; source-specific citation counts remain separate.
- `dist/research-metrics.json`: stored source figures.
- `dist/update-status.json`: last source-check outcome.
- `dist/app.js` / `dist/styles.css`: bilingual UI, filters and styling.
- `site-config.json`: identity and intended site address. If hosting at another address, change `origin` and rebuild.
- `.github/workflows/weekly-site.yml`: independent weekly job, tests and deployment.

## Reliability and maintenance

GitHub Pages hosting and standard GitHub-hosted Actions runners in public repositories are currently available on GitHub Free. Check GitHub's current terms if your usage or account changes. There is no promise of perpetual third-party free hosting. GitHub can disable public scheduled workflows after 60 days without repository activity; review the Actions page if checks stop. The workflow saves meaningful dated update/status records, but this is not a guarantee against provider suspension or policy changes.

A source can be unavailable, rate-limited, incomplete or delayed. Existing records are not deleted when a source fails. New works are accepted only when Crossref's author metadata can establish the identity. A conservative identity check may miss a new work until its author information is complete; the catalogue can also be edited manually.

The site remains readable if an update fails. Source-specific dates identify how current each count is. No visitor database or message-sending backend is included; contact uses ordinary email links.

## Verified references

- GitHub Pages and GitHub Free: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- Actions billing: https://docs.github.com/en/actions/concepts/billing-and-usage
- Scheduled workflow behaviour: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- ORCID public API: https://info.orcid.org/what-is-orcid/services/public-api/
- Crossref REST API: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- Scholar automated-access guidance: https://scholar.google.com/intl/en-US/scholar/help.html
- WoS Researcher API licence/access: https://developer.clarivate.com/apis/wos-researcher
