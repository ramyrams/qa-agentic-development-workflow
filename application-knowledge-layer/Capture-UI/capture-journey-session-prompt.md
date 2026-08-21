You are running a multi-page capture session using the capture-page
approach, across a sequence of pages in one continuous browser session.
I am already logged in where needed / will log in when we reach the
login page — do not attempt to guess credentials.

Sequence for this session:
1. home (unauthenticated)
2. login
3. main-page (after submitting login)
4. catalog-page
5. create-catalog (page or modal — you tell me which once we get there)

For EACH page in the sequence, do the following before moving to the next:

  a. Tell me what action on the previous page brought you here (e.g.
     "clicked login-link", "submitted login-form"). Skip this for home,
     the first page.

  b. Inspect the DOM/accessibility tree. List every interactive element
     with a proposed selector, using this priority: data-testid >
     role+accessible-name > stable CSS > xpath. Tell me the strategy
     used for each.

  c. Screenshot the current state.

  d. Ask me for: purpose (one sentence), any validation rules you
     observed, and test data dependencies for reaching this page. Wait
     for my answer before moving on.

  e. Show me a draft page-record entry (page_id, route, elements,
     purpose, validation_rules, test_data_dependencies) and a draft nav
     edge (from_page, to_page, trigger) linking it to the previous page.
     Don't write files yet — just show me the draft.

  f. Wait for my confirmation ("looks good" or corrections) before
     proceeding to the next page in the sequence.

When we reach "create-catalog": before capturing it, tell me whether
the action opened a new URL (treat as a new page) or a modal/overlay on
the same URL (treat as a new *state* on catalog-page, not a new page) —
ask me to confirm if it's ambiguous.

At the end of the full sequence, output:
  - all draft page records
  - all draft nav edges, in order
  - a draft journey file (ordered list of page_id + action) built from
    the edges above

Do not write any files during this session — everything stays as drafts
in this conversation until I explicitly say "write it."
