---
name: xmos-internal-repo-checks
description: Use when diagnosing or fixing test_repo_checks failures using internal infr_apps scripts, including "repo_checks", "repo checks", "infr_apps checks" or "xmos checks". Requires confirmed applicability of internal checks and access to XMOS infrastructure, not assumed ownership. Source, licence and vendor updates require explicit project authorisation; other checks use applicable update scripts or manual edits.
compatibility: Requires access to the XMOS infr_apps repository and its Python tooling.
---

# XMOS internal repository checks

Diagnose failures from `test_repo_checks` and fix them within the project's confirmed
requirements. Internal checks are not appropriate for every project targeting XMOS devices.

This workflow requires access to the internal `infr_apps` scripts. Confirm that access before
running checks; if it is unavailable, explain the requirement and stop this workflow.

## Ownership and licensing

Confirm that the project actually uses these internal checks before applying their
conventions. Do not infer ownership from repository prefixes, XMOS hardware, organisation
membership, the user's employer, commit history, access to `infr_apps` or licence choice. Customer and
personal projects do not acquire XMOS ownership by using this workflow.

Do not determine legal ownership. Preserve existing copyright, attribution and licence
notices, including third-party notices; do not judge their legitimacy. Source/licence
updaters can insert corporate attribution or replace legal terms. Run them only under
explicit project instructions supplying the notice text or template, licence terms,
affected files and intended changes. Do not investigate ownership to fill missing inputs.
Without such instructions, add no new attribution and leave existing legal metadata
unchanged. Continue ordinary coding without investigating ownership or asking ownership
questions. Ask only when the requested task requires a legal-metadata edit and the
necessary instructions are missing or conflicting. Existing project instructions need
no separate ownership verification.
A failing checker is not authorisation to change copyright, licensing or vendor identity.
Report a checker-policy mismatch rather than forcing a customer project into XMOS templates.

## When to Use

- User reports `test_repo_checks` failures
- User mentions "fix repo checks", "repo_checks", "infr_apps checks"
- Jenkins pipeline fails on "Repo checks" stage
- The project's documented workflow requires these internal repository checks

## Workflow

### 1. DISCOVERY PHASE

After confirming applicability and completing environment setup below, run the test
suite to identify all failing checks:

```bash
pytest <infr_apps>/lib/python/test_repo_checks.py --tb=short --dir=<repo_root>
```

Use absolute paths for both `<infr_apps>` and `<repo_root>`. Repositories are often nested inside
a sandbox checkout, so do not assume `infr_apps` is a sibling of the target repository.

Parse the output to identify which specific checks failed (e.g., `test_check_source`, `test_check_readme`, etc.).

### 2. ENVIRONMENT SETUP

**Check for infr_apps:**

1. Search the target repository's ancestors and sandbox root for an `infr_apps` checkout containing
   `lib/python/test_repo_checks.py`. Prefer the sandbox's canonical checkout over copies embedded in
   unrelated repositories.
2. If not found, clone it alongside the other sandbox repositories, not necessarily beside the
   target repository:
   ```bash
   cd <repo_parent_dir>
   git clone git@github.com:xmos/infr_apps.git
   ```

**Setup Python virtual environment:**

1. First use the target repository's documented environment, if it has one. Otherwise look for an
   existing environment that has the selected `infr_apps` and `infr_scripts_py` dependencies
   installed. The environment name is not authoritative; verify imports before using it.
2. Verify the candidate environment:
   ```bash
   source <venv>/bin/activate
   PYTHONPATH=<infr_apps>/lib/python python -c "import xmos_source_check; from build_system.repo_type import RepoType"
   ```
3. If no compatible environment exists, create `.venv_<repo_name>` and install the selected
   `infr_apps` checkout:
   ```bash
   python3 -m venv .venv_<repo_name>
   source .venv_<repo_name>/bin/activate
   pip install <infr_apps>
   ```

**Set PYTHONPATH:**
```bash
export PYTHONPATH=<infr_apps>/lib/python:$PYTHONPATH
```

If pytest reports that `--dir` is unrecognized, the wrong test file was selected or its adjacent
`conftest.py` is missing. Do not drop `--dir`; locate a complete, current `infr_apps` checkout.

### 3. CONFIRM LEGAL-METADATA SCOPE

Before any source or licence update:

1. Read the project's supplied notice policy and preserve existing notices and licence
   files. Do not classify files by apparent ownership. Exclude every file not explicitly
   covered by the supplied update scope, including vendored and generated files.
2. Require explicit project instructions supplying the notice text or template, licence
   terms, file scope and intended changes. Do not verify ownership independently.
   A request to "fix repo checks" alone is insufficient.
3. Inspect the selected updater and its templates to confirm that its behaviour matches
   that authorisation. If it cannot preserve required holders or terms, do not run it;
   report the mismatch and ask about an appropriate checker configuration or scoped edit.
4. Treat configuration as the current setup, not as a substitute for notice instructions.
   If the supplied instructions are missing or conflicting, leave legal metadata unchanged
   and ask only about the required edit. Do not choose a holder, vendor or licence yourself.

For diagnosis, inspect a licence type when explicitly configured:

```bash
# Extract license type when explicitly configured
grep "^license:" settings.yml
```

Not every repository declares `license` in `settings.yml`; inspect its existing licence
files and the selected tool's accepted values. Matching a licence to a tool value does
not satisfy the authorisation gate above. Flag potential licensing or confidentiality
conflicts for the project owner without choosing different terms or rewriting notices.

### 4. FIX EACH FAILING CHECK

Process each failing check according to its type:

---

#### SCRIPTED CHECKS (Subject to Project Authorisation)

These checks have built-in `update` modes. Classify their effects before using them;
source and licence updates require the section 3 gate, even if the checker calls them fixable.

##### `test_check_source` - Copyright Headers

**What it checks:** Source files (.c, .h, .py, .xc, etc.) have correct copyright headers with accurate dates and license references.

**Authorisation required:** Complete section 3 before running this command. Check that
the selected script's exact notice text and file scope match the project's supplied
instructions; otherwise leave notices unchanged and report the mismatch.

**Conditional command (not a default fix):**
```bash
python <infr_apps>/lib/python/xmos_source_check.py update <repo_path> <project_supplied_license_type>
```

**What it does:**
- Adds missing copyright headers
- Updates copyright date ranges based on git history
- Fixes license reference text to match the template

Review the full diff for added, replaced or duplicated legal notices before rerunning
`test_check_source`. A reported old or duplicate notice is not permission to remove it.
Preserve existing copyright, third-party attribution and licence terms; remove or replace
a notice only where the supplied instructions explicitly cover it, not your ownership judgement.

**Common errors:**
- `"File /path/to/file.c does not have current copyright at start of file"`
- `"Copyright date range incorrect"`

**Note:** Some files may be ignored via `.xmos_ignore_source_check` or `.xmos/.xmos_ignore_source_check`.

---

##### `test_check_license` - LICENSE.rst File

**What it checks:** `LICENSE.rst` or `LICENSE.txt` matches the expected template for the license type in `settings.yml`.

**Authorisation required:** Complete section 3 before running this command. Compare the
updater's licence terms, file scope and exact template with the supplied project instructions.
Missing or mismatched licence files are not permission to choose terms or a holder.

**Conditional command (not a default fix):**
```bash
python <infr_apps>/lib/python/xmos_license_check.py update <repo_path>
```

**What it does:**
- Reads license type from `settings.yml`
- Writes the correct LICENSE.rst template

Review the diff against the approved terms. Preserve existing licence files and their
scope; do not delete additional licences or third-party notices to make this check pass.

**Common errors:**
- `"License file LICENSE.rst is incorrect"`
- `"Missing LICENSE.rst"`

---

##### `test_check_changelog` - CHANGELOG.rst Formatting

**What it checks:** `CHANGELOG.rst` has correct RST formatting, version entries, and dependency tracking.

**How to fix:**
```bash
cd ../infr_apps/lib/python
python xmos_changelog_check.py update <repo_path>
# Example: python xmos_changelog_check.py update ../../lib_sw_pll
```

**What it does:**
- Fixes RST formatting (bullet points, underlines)
- Adds missing version entries
- Updates dependency version tracking

**Common errors:**
- `"CHANGELOG.rst doesn't start with current version"`
- `"Line X does not match expected format"`
- `"Dependency version mismatch"`

---

#### MANUAL-FIX CHECKS (AI Edits Based on Error Messages)

These checks require manual editing based on error analysis:

##### `test_check_readme` - README.rst Structure

**What it checks:** README.rst structure, required sections, title format, RST syntax.

**How to fix:** Edit `README.rst` based on error messages.

**Conventions:** follow [README.rst](../xmos-library-repo-style/SKILL.md#readmerst)
in the style skill for title format, metadata and section order. Run an RST checker
(for example `rstcheck README.rst`) for syntax errors.

**Error patterns:**
- `"readme_check: Title doesn't match expected..."`
- `"Missing section: Features"`
- `"RST syntax error at line X"`

**Fix approach:**
- Read the error message carefully
- Fix structure/syntax within the project's adopted conventions; preserve legal and
  vendor metadata unless explicit project instructions supply the required changes

---

##### `test_check_settings` - settings.yml Schema

**What it checks:** `settings.yml` schema validation, version format, cognidox numbers, doxygen config.

**How to fix:** Edit `settings.yml` based on error messages.

**Conventions:** follow [settings.yml](../xmos-library-repo-style/SKILL.md#settingsyml)
in the style skill and the schema enforced by the selected `infr_apps` revision. Use
the repository's existing structure; do not invent Cognidox part numbers.

**Error patterns:**
- `"settings.yml doesn't match basic schema"`
- `"Invalid version format"`
- `"Missing cognidox part numbers"`

**Fix approach:**
- Read the full `settings.yml` file
- Compare against the schema requirements in the error message
- Add missing non-legal fields or fix invalid values within confirmed project requirements
- A missing or invalid `license` or vendor field requires the section 3 gate, not a default

---

##### `test_check_versions` - Version Consistency

**What it checks:** Version numbers are consistent across README.rst, settings.yml, CHANGELOG.rst, and lib_build_info.cmake.

**How to fix:** Synchronize versions across all files.

**Files to check** (see [version consistency](../xmos-library-repo-style/SKILL.md#version-consistency)):
1. `README.rst` - `:version:` metadata field
2. `settings.yml` - `version:` field
3. `CHANGELOG.rst` - First version entry
4. `lib_build_info.cmake` - `set(LIB_VERSION "X.Y.Z")`

**Error patterns:**
- `"Version mismatch: README.rst: 1.0.0, settings.yml: 1.0.1"`

**Fix approach:**
- Identify the correct version (typically from settings.yml)
- Update all other files to match
- This may require multiple iterations as fixing one file affects version check

---

##### `test_check_metadata` - README.rst Metadata

**What it checks:** Metadata block in README.rst is parseable and contains valid field values.

**How to fix:** Edit the metadata block in README.rst.

**Metadata format:**
```rst
:vendor: <project-supplied vendor value, if required>
:version: 1.0.0
:scope: General Use
:description: Software PLL library
:category: DSP
:keywords: PLL, clock recovery, synchronization
```

**Common issues:**
- Invalid field names
- Incorrect field values
- Malformed RST field list syntax

**Error patterns:**
- `"metadata_check: Failed to parse metadata"`
- `"Invalid metadata field: X"`

**Fix approach:**
- Locate the metadata block in README.rst (typically after the title)
- Fix syntax or field values based on error message
- Ensure proper RST field list format (`:field: value`)
- Preserve existing vendor metadata; use only a project-supplied value for a new field.
  If a required value is missing or conflicts with the checker, report it and ask about
  that edit rather than inferring a vendor; vendor is not the copyright holder

---

##### `test_check_documentation` - doc/rst/ Structure

**What it checks:** Documentation folder structure, proper includes, README.rst not included in user guide.

**How to fix:** Create/fix doc/rst/ structure.

**Required structure:**
```
doc/
└── rst/
    ├── user_guide.rst      # Main user guide
    └── ...                 # Other documentation
```

**Common issues:**
1. Missing `doc/` or `doc/rst/` folders
2. README.rst incorrectly included in user guide

**Error patterns:**
- `"Missing doc/ folder"`
- `"User guide document includes README.rst"`

**Fix approach:**
- Create missing directories if needed
- Remove README.rst includes from user guide
- Ensure proper RST structure in documentation

---

##### `test_check_deps` - Dependency Versions

**What it checks:** Dependencies have version specifications in `module_build_info` and `lib_build_info.cmake`.

**How to fix:** Edit build files to add version specifications.

**module_build_info format:**
```
DEPENDENT_MODULES = lib_logging(>=2.0.0) lib_xassert(>=4.0.0)
```

**lib_build_info.cmake format:**
```cmake
set(LIB_NAME lib_sw_pll)
set(LIB_VERSION "1.0.0")
set(LIB_DEPENDENT_MODULES "lib_logging(2.0.0)" "lib_xassert(4.0.0)")
```

These versions illustrate the syntax; use versions verified for the repository.
CMake entries are individually quoted exact references, not the legacy Makefile's
minimum-version expressions. See
[dependency version pinning](../xmos-library-repo-style/SKILL.md#dependency-version-pinning).

**Common issues:**
- Dependencies without version specifications
- Invalid version format

**Error patterns:**
- `"module_build_info dependency lib_logging does not specify version"`
- `"Invalid version format in lib_build_info.cmake"`

**Fix approach:**
- Identify dependencies without versions
- Determine appropriate version constraints (check dependent library versions)
- Add version specifications in proper format

---

##### `test_check_compiler_flags` - Debug Flags (APPLICATION_NOTE only)

**What it checks:** APP_COMPILER_FLAGS contains `-g` flag for debug symbols.

**How to fix:** Edit Makefile or CMakeLists.txt to add `-g` flag.

**Note:** This check only applies to APPLICATION_NOTE repositories, not LIBRARY repos.

**Error patterns:**
- `"Compiler flags check FAILED: Debug symbols flag '-g' is missing"`

**Fix approach:**
- Locate APP_COMPILER_FLAGS definition
- Add `-g` flag

---

### 5. VERIFY FIX

After fixing each check, re-run the specific test to verify:

```bash
pytest <infr_apps>/lib/python/test_repo_checks.py::test_check_<name> --tb=short --dir=<repo_root>
# Example: pytest <infr_apps>/lib/python/test_repo_checks.py::test_check_source --tb=short --dir=<repo_root>
```

If the check still fails, analyze the new error message within the confirmed scope.
Do not broaden legal-metadata edits to obtain a passing check; report blocked mismatches.

### 6. FINAL VERIFICATION

After all fixes are applied, run all originally-failing checks again:

```bash
pytest <infr_apps>/lib/python/test_repo_checks.py --tb=short --dir=<repo_root>
```

### 7. SUMMARY

Report to the user:

1. **Files modified** (all uncommitted for review):
   - List each file changed
   - Briefly describe what was fixed

2. **Checks fixed:**
   - List each test that now passes

3. **Remaining issues** (if any):
   - List checks that still fail
   - Explain what manual intervention might be needed

4. **Next steps:**
   - User should review changes with `git diff`
   - User should commit when satisfied
   - Suggest running full test suite if available

## Repository Type Skip Logic

Some checks are skipped based on repository type (from settings.yml):

- **APPLICATION_NOTE**: Skips `test_check_deps`, adds compiler flags check
- **DOCUMENTATION**: Skips `test_check_license`, `test_check_readme`, `test_check_metadata`
- **REFERENCE_DESIGN**: Skips `test_check_license`, `test_check_readme`, `test_check_settings`, `test_check_documentation`, `test_check_versions`
- **LIBRARY** (most repos): Runs all checks except `test_check_compiler_flags`

## Important Notes

1. **DO NOT commit changes** - Leave all modifications uncommitted for user review
2. **Iterative fixes** - Some checks (especially versions) may require multiple passes
3. **Legal-metadata gate** - Checker failures never authorise ownership or licensing changes
4. **Ignore files** - Source check respects `.xmos_ignore_source_check` patterns
5. **Virtual environment** - Always use `.venv_<repo_name>` convention for consistency

## Reference Paths

- **Test file:** `<infr_apps>/lib/python/test_repo_checks.py`
- **Check scripts:** `../infr_apps/lib/python/xmos_*_check.py`
- **Repository root:** Current working directory when skill is invoked

## Troubleshooting

**If infr_apps clone fails:**
- Check SSH key is set up for GitHub
- Try HTTPS: `git clone https://github.com/xmos/infr_apps.git`

**If pytest can't find test_repo_checks.py:**
- Verify PYTHONPATH includes `../infr_apps/lib/python`
- Check infr_apps was cloned successfully

**If venv activation fails:**
- Ensure Python 3 is installed
- Try creating fresh venv: `rm -rf .venv_<repo_name> && python3 -m venv .venv_<repo_name>`

**If update scripts fail:**
- Check you're running from infr_apps/lib/python directory
- Verify repository path is correct (relative paths from infr_apps/lib/python)
- Check license type is valid (xmos_public_v1, xmos_old, vocalfusion3600, etc.)
