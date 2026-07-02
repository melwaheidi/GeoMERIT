# GeoMERIT release checklist

This guide walks through publishing the GeoMERIT code release on GitHub and
archiving it on Zenodo so it receives a citable DOI. Steps that require your
authenticated accounts are marked **[you]**; everything in the repository is
already prepared.

There is one decision to make first (Step 0), then GitHub (Steps 1-4), then the
one-time Zenodo link (Step 5), then the archive itself (Steps 6-8).

---

## Step 0 - Reconcile the DOI **[you, important]**

The manuscript's data-availability statement currently cites a Zenodo **concept
DOI** of `10.5281/zenodo.20932723`. A concept DOI always points to the latest
version and is minted by Zenodo the first time a record is archived.

- **If that concept DOI already exists** (you archived an earlier version of
  GeoMERIT under it): good, keep it. When you archive this release as a new
  version, Zenodo mints a new *version* DOI under that same concept DOI, and the
  manuscript's concept-DOI citation stays valid. Proceed as written.
- **If that concept DOI does not yet exist** (this is the first archive): Zenodo
  will assign a concept DOI only when you publish (Step 7). It will very likely
  NOT equal 20932723. In that case, after Step 7 you must update the DOI in the
  manuscript (data-availability statement), `CITATION.cff`, and README to the
  real concept DOI, then use that corrected manuscript for submission.

Do not submit the manuscript to the journal until the DOI it prints matches the
DOI Zenodo actually assigns.

---

## Step 1 - Prepare the local repository **[you]**

From the folder containing the GeoMERIT files:

```
git init                       # if not already a git repo
git add .
git commit -m "GeoMERIT v1.0.0: tool, benchmark, reproduction scripts, manuscript"
```

Confirm these release files are present and committed:

- `geophysical_method_selector.py`, `benchmark_cases.csv`, and all `run_*.py`,
  `make_*.py`, `reproduce.py`, `test_geomerit.py`
- `GeoMERIT_demo.ipynb`, `requirements.txt`, `LICENSE`, `README.md`, `USAGE.md`
- `CITATION.cff` and `.zenodo.json` (both prepared for you)
- `references.json` (the verified reference list)
- `MANUSCRIPT_GeoMERIT_v3.docx` (optional in the repo; remove if you prefer the
  code archive to exclude the manuscript)

Quick pre-flight (optional but recommended):

```
pip install -r requirements.txt
python test_geomerit.py        # expect 8/8 passed
python reproduce.py            # regenerates every result and figure
```

## Step 2 - Create the GitHub repository **[you]**

If `https://github.com/melwaheidi/GeoMERIT` does not yet exist, create it on
GitHub (public, no auto-generated README/license since the repo already has
them). Then point your local repo at it:

```
git branch -M main
git remote add origin https://github.com/melwaheidi/GeoMERIT.git
git push -u origin main
```

If the repo already exists with older contents, push these files to update it
(force only if you intend to replace history):

```
git push origin main
```

## Step 3 - Verify the repository renders correctly **[you]**

On the GitHub repo page, confirm:

- `README.md` renders and the title matches the manuscript.
- A "Cite this repository" button appears on the right sidebar (this confirms
  `CITATION.cff` parsed correctly).
- `LICENSE` is detected as MIT.

## Step 4 - Tag and create the release **[you]**

Create an annotated tag and push it:

```
git tag -a v1.0.0 -m "GeoMERIT v1.0.0"
git push origin v1.0.0
```

Then on GitHub: **Releases -> Draft a new release**.

- Choose tag `v1.0.0`.
- Release title: `GeoMERIT v1.0.0`.
- Description: a short summary (for example, the abstract's first two sentences,
  plus the headline benchmark result: deployed method within the top-three
  shortlist in 82% of 22 documented cases).
- **Do not publish yet if you still need to complete Step 5** (the Zenodo link
  must exist before the release is published, or Zenodo will not capture it).

---

## Step 5 - Link GitHub to Zenodo (one time) **[you]**

Only needed once per account.

1. Sign in to `https://zenodo.org` (use "Log in with GitHub" or connect the
   account under **Account -> Linked accounts -> GitHub**).
2. Go to `https://zenodo.org/account/settings/github/`.
3. Find `melwaheidi/GeoMERIT` in the repository list and toggle it **ON**.
   (If it does not appear, use "Sync now" to refresh, then toggle it.)

This tells Zenodo to watch the repo and archive any new GitHub release.

## Step 6 - Publish the release to trigger archiving **[you]**

Back on the GitHub release draft from Step 4, click **Publish release**.

Zenodo detects the published release (with the toggle ON from Step 5) and
automatically creates an archive using the metadata in `.zenodo.json` (title,
author, ORCID, license, keywords). This usually completes within a few minutes.

## Step 7 - Confirm the Zenodo record and DOI **[you]**

1. Return to `https://zenodo.org/account/settings/github/` (or your Zenodo
   uploads). The repository now shows a DOI badge.
2. Open the record and confirm:
   - Title, author name, and ORCID are correct (from `.zenodo.json`).
   - License shows MIT.
   - The uploaded archive contains the release files.
3. Note the two DOIs Zenodo shows:
   - the **version DOI** (specific to v1.0.0), and
   - the **concept DOI** (the "Cite all versions" DOI).
   The manuscript should cite the **concept DOI**.

## Step 8 - Final reconciliation and submission **[you]**

- If the concept DOI equals `10.5281/zenodo.20932723`, the manuscript is already
  correct; proceed to submit.
- If it differs, update the concept DOI in the manuscript's data-availability
  statement, in `CITATION.cff` (the `preferred-citation` / archive DOI), and in
  `README.md`, commit those edits, and if desired publish a small patch release
  (`v1.0.1`) so the archived copy also carries the corrected DOI. Then submit the
  corrected manuscript to Applied Computing and Geosciences with the cover letter
  and highlights.

---

## Notes

- Anthropic tools cannot perform the GitHub push or the Zenodo archive; both
  require your authenticated accounts. This checklist is the hand-off.
- Every subsequent GitHub release you publish (v1.0.1, v1.1.0, and so on) will be
  archived automatically under the same concept DOI, so future updates need only
  Steps 1, 4, and 6.
- Keep the repository public; a private repo cannot be archived by Zenodo.
