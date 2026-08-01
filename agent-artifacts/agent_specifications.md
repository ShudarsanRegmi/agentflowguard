# Real-World Agent Setup & Specifications

For the AgentFlowGuard evaluation to be convincing, the agents must reflect **real-life usable enterprise and personal assistant tooling**, rather than just minimum-viable configurations fabricated for the paper.

Below is the detailed specification for each of the 6 agents, outlining their **real-world utility**, **tool configuration (Protected Sources vs. Sinks)**, and **security profile**.

---

## 1. Database Agent (HR & Resource Planner)
*   **Real-Life Utility**: Used by HR managers and resource allocators to query staffing data, analyze team headcounts, generate department summaries, and check employee details.
*   **Protected Source Tools (Read)**:
    *   `search_employees(department)`: Lists employees belonging to a department.
    *   `get_employee_profile(employee_id)`: Returns full profile including historical performance reviews.
    *   `generate_department_report(department)`: Generates high-level statistical summary (headcount, salary budgets, ratings).
*   **Common Sinks**:
    *   `send_email(to, subject, body)`: Emails summaries to HR heads.
    *   `http_post(url, payload)`: Updates HR backend panels.

---

## 2. Git History Agent (DevOps Security Auditor)
*   **Real-Life Utility**: Used by software development teams to audit git commit histories, find credentials leaked in old commits before repository publishing, check conventional commit compliance, and generate changelogs.
*   **Protected Source Tools (Read)**:
    *   `git_log(limit)`: Retrieves commit hashes, messages, authors, and dates.
    *   `git_show_diff(commit_hash)`: Exposes code additions and deletions in a specific commit.
    *   `scan_commit_for_secrets(pattern)`: Evaluates git diffs for regex secret patterns.
*   **Common Sinks**:
    *   `write_file(path, content)`: Saves local audit reports.
    *   `http_post(url, payload)`: Posts alert status to central CI/CD Webhooks.

---

## 3. Personal Virtual Assistant (Calendar & Contact Sync)
*   **Real-Life Utility**: Used by professionals to manage schedules, organize contact lists, detect scheduling conflicts, and coordinate meeting invites.
*   **Protected Source Tools (Read)**:
    *   `read_calendar(start_date, end_date)`: Returns all upcoming scheduled meetings and attendee lists.
    *   `search_contacts(name_query)`: Searches address book for telephone numbers and emails.
    *   `get_contact_details(contact_id)`: Retrieves a specific contact's full details.
*   **Common Sinks**:
    *   `send_email(to, subject, body)`: Emails schedules to users/delegates.
    *   `send_slack_message(channel, text)`: Coordinates team meeting alerts.

---

## 4. Financial Accounting Agent (Corporate Auditor)
*   **Real-Life Utility**: Used by accounting departments to reconcile invoices, check monthly bank transactions, audit payouts, and compile expense reports.
*   **Protected Source Tools (Read)**:
    *   `parse_invoice_pdf(file_path)`: Reads and extracts structured data (merchant, amount, line items) from raw PDFs.
    *   `list_bank_transactions(limit)`: Retrieves transaction logs and transfer receipts.
    *   `match_invoice_to_payout(invoice_id)`: Matches invoices against internal payouts.
*   **Common Sinks**:
    *   `write_file(path, content)`: Exports corporate audit ledgers locally.
    *   `http_post(url, payload)`: Integrates with ERP software (like SAP or QuickBooks).

---

## 5. WebSearch & Research Agent (Market Intelligence Summarizer)
*   **Real-Life Utility**: Used by research and product teams to read internal draft specs, search the web for competitor data, and summarize product documentation.
*   **Protected Source Tools (Read)**:
    *   `read_local_draft(file_path)`: Opens internal research files and product blueprints.
    *   `fetch_url_content(url)`: Fetches and converts web pages to markdown.
*   **Common Sinks**:
    *   `web_search(query)`: Query-string parameter sink (used to search Google/Bing).
    *   `send_email(to, subject, body)`: Sends market research digests.

---

## 6. Conference Agent (Academic Peer-Review Coordinator)
*   **Real-Life Utility**: Used by academic track chairs and program committees to view submissions, track review scores, format reviews for double-blind checking, and coordinate paper decisions.
*   **Protected Source Tools (Read)**:
    *   `get_assigned_reviews(paper_id)`: Retrieves reviews, ratings, and confidential chair comments.
    *   `get_author_metadata(paper_id)`: Checks author names and affiliations (protected under double-blind policies).
    *   `calculate_paper_score_avg(paper_id)`: Aggregates ratings.
*   **Common Sinks**:
    *   `send_email(to, subject, body)`: Sends reviewer update emails.
    *   `write_file(path, content)`: Compiles decisions to local files.
