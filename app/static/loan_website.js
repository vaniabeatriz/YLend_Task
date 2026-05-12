const loanApiPath = "/loans";
const localFeedbackTargetMs = 2000;

const feedbackClasses = {
  success: "alert-success",
  validation: "alert-danger",
  duplicate: "alert-warning",
  "not-found": "alert-warning",
  empty: "alert-info",
  loading: "alert-info",
  "service-unavailable": "alert-danger",
  authentication: "alert-warning",
  setup: "alert-danger",
};

const moneyFormatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const state = {
  activeAction: null,
  auth: {
    authenticated: false,
    user: null,
    accessToken: null,
    setupError: null,
  },
};

function getElement(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showFeedback(type, message, details = []) {
  const feedback = getElement("global-feedback");
  if (!feedback) {
    return;
  }

  const className = feedbackClasses[type] || "alert-secondary";
  const detailList = details.length
    ? `<ul>${details
        .map((detail) => `<li>${escapeHtml(detail.message || detail)}</li>`)
        .join("")}</ul>`
    : "";

  feedback.className = `alert ${className}`;
  feedback.dataset.feedbackType = type;
  feedback.dataset.feedbackTargetMs = String(localFeedbackTargetMs);
  feedback.innerHTML = `<strong>${escapeHtml(message)}</strong>${detailList}`;
}

function showFieldErrors(containerId, details = []) {
  const container = getElement(containerId);
  if (!container) {
    return;
  }

  if (!details.length) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `<ul>${details
    .map((detail) => `<li>${escapeHtml(detail.message || detail)}</li>`)
    .join("")}</ul>`;
}

function setActionControlsDisabled(disabled) {
  document
    .querySelectorAll("[data-action-control]")
    .forEach((control) => {
      control.disabled = disabled;
      control.setAttribute("aria-disabled", String(disabled));
    });
}

function startAction(action, message) {
  if (state.activeAction) {
    showFeedback("loading", "An action is already in progress.");
    return false;
  }

  state.activeAction = action;
  document.body.dataset.activeAction = action;
  setActionControlsDisabled(true);
  showFeedback("loading", message);
  return true;
}

function finishAction() {
  state.activeAction = null;
  delete document.body.dataset.activeAction;
  setActionControlsDisabled(false);
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return {};
  }

  return response.json();
}

async function requestJson(path, options = {}) {
  let response;
  const requestOptions = { ...options };
  const headers = { ...(options.headers || {}) };

  if (path.startsWith(loanApiPath) && state.auth.accessToken) {
    headers.Authorization = `Bearer ${state.auth.accessToken}`;
  }

  if (Object.keys(headers).length) {
    requestOptions.headers = headers;
  }

  try {
    response = await fetch(path, requestOptions);
  } catch (error) {
    const serviceError = new Error("The loan service is unavailable. Check the running Flask app and retry.");
    serviceError.kind = "service-unavailable";
    throw serviceError;
  }

  const payload = await parseResponse(response);

  if (!response.ok) {
    const apiError = new Error(payload.message || "The loan action could not be completed.");
    apiError.status = response.status;
    apiError.payload = payload;
    apiError.kind = payload.error;
    throw apiError;
  }

  return payload;
}

function errorFeedback(error, fallbackMessage) {
  if (error.kind === "service-unavailable") {
    return {
      type: "service-unavailable",
      message: error.message,
      details: [],
    };
  }

  if (error.kind === "validation_error") {
    return {
      type: "validation",
      message: error.payload.message || fallbackMessage,
      details: error.payload.details || [],
    };
  }

  if (error.kind === "duplicate_loan_id") {
    return {
      type: "duplicate",
      message: error.payload.message || "A loan with this loan ID already exists.",
      details: [],
    };
  }

  if (error.kind === "loan_not_found") {
    return {
      type: "not-found",
      message: error.payload.message || "No loan exists for this loan ID.",
      details: [],
    };
  }

  if (
    error.kind === "authentication_required" ||
    error.kind === "invalid_token"
  ) {
    return {
      type: "authentication",
      message: error.payload.message || "Sign in again to continue.",
      details: [],
    };
  }

  if (error.kind === "auth_configuration_error") {
    return {
      type: "setup",
      message: error.payload.message || "Auth0 setup is incomplete.",
      details: error.payload.details || [],
    };
  }

  return {
    type: "service-unavailable",
    message: fallbackMessage,
    details: [],
  };
}

function signedInLabel(user) {
  if (!user) {
    return "Signed in.";
  }

  return `Signed in as ${user.name || user.email || "authenticated user"}.`;
}

function resetWorkflowSections() {
  document
    .querySelectorAll("[data-workflow-section]")
    .forEach((section) => {
      section.hidden = true;
    });

  document
    .querySelectorAll("[data-section-target]")
    .forEach((button) => {
      button.setAttribute("aria-expanded", "false");
    });
}

function applyAuthState(authState) {
  state.auth = {
    authenticated: Boolean(authState.authenticated),
    user: authState.user || null,
    accessToken: authState.accessToken || null,
    setupError: authState.setupError || null,
  };

  document.body.dataset.authenticated = String(state.auth.authenticated);

  document
    .querySelectorAll("[data-auth-required]")
    .forEach((element) => {
      element.hidden = !state.auth.authenticated;
    });

  document
    .querySelectorAll("[data-auth-signed-out]")
    .forEach((element) => {
      element.hidden = state.auth.authenticated;
    });

  document
    .querySelectorAll("[data-auth-signed-in]")
    .forEach((element) => {
      element.hidden = !state.auth.authenticated;
    });

  const status = getElement("auth-status");
  if (status) {
    if (state.auth.authenticated) {
      status.textContent = signedInLabel(state.auth.user);
    } else if (state.auth.setupError) {
      status.textContent = state.auth.setupError;
    } else {
      status.textContent = "Sign in to use loan workflows.";
    }
  }

  if (!state.auth.authenticated) {
    resetWorkflowSections();
  }
}

async function loadAuthStatus() {
  try {
    const authState = await requestJson("/auth/status", { method: "GET" });
    applyAuthState(authState);
    if (!authState.authenticated && authState.setupError) {
      showFeedback("setup", authState.setupError);
    }
  } catch (error) {
    applyAuthState({ authenticated: false });
    showFeedback("service-unavailable", "Authentication status could not be loaded.");
  }
}

function requireSignedIn() {
  if (state.auth.authenticated) {
    return true;
  }

  showFeedback(
    state.auth.setupError ? "setup" : "authentication",
    state.auth.setupError || "Sign in to use loan workflows."
  );
  resetWorkflowSections();
  return false;
}

function loanMarkup(loan) {
  return `
    <article class="loan-row" data-loan-id="${escapeHtml(loan.loanId)}">
      <div class="loan-attribute">
        <span>Loan ID</span>
        <strong>${escapeHtml(loan.loanId)}</strong>
      </div>
      <div class="loan-attribute">
        <span>Borrower</span>
        <strong>${escapeHtml(loan.borrowerName)}</strong>
      </div>
      <div class="loan-attribute">
        <span>Funding</span>
        <strong>${moneyFormatter.format(loan.fundingAmount)}</strong>
      </div>
      <div class="loan-attribute">
        <span>Repayment</span>
        <strong>${moneyFormatter.format(loan.repaymentAmount)}</strong>
      </div>
    </article>
  `;
}

function renderLoanCollection(containerId, loans, emptyMessage) {
  const container = getElement(containerId);
  if (!container) {
    return;
  }

  if (!loans.length) {
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyMessage)}</p>`;
    return;
  }

  container.innerHTML = loans.map(loanMarkup).join("");
}

function renderSingleLoan(containerId, loan) {
  const container = getElement(containerId);
  if (!container) {
    return;
  }

  container.innerHTML = loanMarkup(loan);
}

function renderEmptyState(containerId, message) {
  const container = getElement(containerId);
  if (!container) {
    return;
  }

  container.innerHTML = `<p class="empty-state">${escapeHtml(message)}</p>`;
}

function removeLoanFromVisibleResults(loanId) {
  ["borrower-results", "lookup-result"].forEach((containerId) => {
    const container = getElement(containerId);
    if (!container) {
      return;
    }

    container
      .querySelectorAll(".loan-row")
      .forEach((row) => {
        if (row.dataset.loanId === loanId) {
          row.remove();
        }
      });

    if (!container.querySelector(".loan-row") && containerId === "borrower-results") {
      renderEmptyState(containerId, "No loans match this borrower name.");
    }

    if (!container.querySelector(".loan-row") && containerId === "lookup-result") {
      renderEmptyState(containerId, "No loan exists for this loan ID.");
    }
  });
}

function showWorkflowSection(sectionId) {
  if (!requireSignedIn()) {
    return;
  }

  document
    .querySelectorAll("[data-workflow-section]")
    .forEach((section) => {
      section.hidden = section.id !== sectionId;
    });

  document
    .querySelectorAll("[data-section-target]")
    .forEach((button) => {
      button.setAttribute(
        "aria-expanded",
        String(button.dataset.sectionTarget === sectionId)
      );
    });

  const selectedSection = getElement(sectionId);
  if (selectedSection) {
    selectedSection.scrollIntoView({ block: "start", behavior: "smooth" });
  }

  if (sectionId === "current-loans-section") {
    loadCurrentLoans();
  }
}

async function loadCurrentLoans({ announceSuccess = false } = {}) {
  if (!requireSignedIn()) {
    const status = getElement("current-loans-status");
    if (status) {
      status.textContent = "Sign in to load current loans.";
    }
    return;
  }

  const status = getElement("current-loans-status");
  if (status) {
    status.textContent = "Loading current loans.";
  }

  try {
    const payload = await requestJson(loanApiPath, { method: "GET" });
    const loans = payload.loans || [];
    renderLoanCollection(
      "current-loans",
      loans,
      "No current loans for this session."
    );

    if (status) {
      status.textContent = loans.length
        ? `${loans.length} current loan${loans.length === 1 ? "" : "s"} loaded.`
        : "No current loans for this session.";
    }

    if (announceSuccess) {
      showFeedback("success", "Current loans refreshed.");
    }
  } catch (error) {
    const feedback = errorFeedback(error, "Current loans could not be loaded.");
    showFeedback(feedback.type, feedback.message, feedback.details);
    if (status) {
      status.textContent = "Current loans could not be loaded.";
    }
  }
}

function preserveCreateFormValues() {
  const form = getElement("create-loan-form");
  const data = new FormData(form);
  return {
    loanId: data.get("loanId"),
    borrowerName: data.get("borrowerName"),
    fundingAmount: data.get("fundingAmount"),
    repaymentAmount: data.get("repaymentAmount"),
  };
}

function restoreCreateFormValues(values) {
  const form = getElement("create-loan-form");
  Object.entries(values).forEach(([key, value]) => {
    const input = form.elements.namedItem(key);
    if (input) {
      input.value = value;
    }
  });
}

function createPayloadFromForm(form) {
  const data = new FormData(form);
  return {
    loanId: data.get("loanId"),
    borrowerName: data.get("borrowerName"),
    fundingAmount: Number(data.get("fundingAmount")),
    repaymentAmount: Number(data.get("repaymentAmount")),
  };
}

async function handleCreateLoan(event) {
  event.preventDefault();

  if (!startAction("create", "Creating loan.")) {
    return;
  }

  const form = event.currentTarget;
  const preservedValues = preserveCreateFormValues();
  showFieldErrors("create-loan-errors");

  try {
    const createdLoan = await requestJson(loanApiPath, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(createPayloadFromForm(form)),
    });

    form.reset();
    await loadCurrentLoans();
    showFeedback("success", `Created loan ${createdLoan.loanId}.`);
  } catch (error) {
    restoreCreateFormValues(preservedValues);
    const feedback = errorFeedback(error, "Loan could not be created.");
    showFieldErrors("create-loan-errors", feedback.details);
    showFeedback(feedback.type, feedback.message, feedback.details);
  } finally {
    finishAction();
  }
}

async function handleBorrowerSearch(event) {
  event.preventDefault();

  if (!startAction("search", "Searching current loans by borrower name.")) {
    return;
  }

  const form = event.currentTarget;
  const data = new FormData(form);
  const borrowerName = data.get("borrowerName") || "";
  const status = getElement("borrower-results-status");
  showFieldErrors("borrower-search-errors");

  try {
    const params = new URLSearchParams({ borrowerName });
    const payload = await requestJson(`${loanApiPath}?${params.toString()}`, {
      method: "GET",
    });
    const loans = payload.loans || [];
    renderLoanCollection(
      "borrower-results",
      loans,
      "No loans match this borrower name."
    );

    if (status) {
      status.textContent = loans.length
        ? `${loans.length} borrower match${loans.length === 1 ? "" : "es"} loaded.`
        : "No loans match this borrower name.";
    }

    showFeedback(
      loans.length ? "success" : "empty",
      loans.length
        ? `Found ${loans.length} current loan${loans.length === 1 ? "" : "s"} for ${borrowerName.trim()}.`
        : "No loans match this borrower name."
    );
  } catch (error) {
    const feedback = errorFeedback(error, "Borrower search could not be completed.");
    showFieldErrors("borrower-search-errors", feedback.details);
    showFeedback(feedback.type, feedback.message, feedback.details);
    if (status) {
      status.textContent = "Borrower search could not be completed.";
    }
  } finally {
    finishAction();
  }
}

async function handleLoanLookup(event) {
  event.preventDefault();

  if (!startAction("lookup", "Looking up loan by loan ID.")) {
    return;
  }

  const form = event.currentTarget;
  const data = new FormData(form);
  const loanId = data.get("loanId") || "";
  const status = getElement("lookup-result-status");
  showFieldErrors("loan-lookup-errors");

  try {
    const loan = await requestJson(`${loanApiPath}/${encodeURIComponent(loanId)}`, {
      method: "GET",
    });
    renderSingleLoan("lookup-result", loan);
    if (status) {
      status.textContent = `Loan ${loan.loanId} loaded.`;
    }
    showFeedback("success", `Found loan ${loan.loanId}.`);
  } catch (error) {
    const feedback = errorFeedback(error, "Loan lookup could not be completed.");
    showFieldErrors("loan-lookup-errors", feedback.details);
    if (feedback.type === "not-found") {
      renderEmptyState("lookup-result", "No loan exists for this loan ID.");
    }
    showFeedback(feedback.type, feedback.message, feedback.details);
    if (status) {
      status.textContent = feedback.message;
    }
  } finally {
    finishAction();
  }
}

async function handleLoanDelete(event) {
  event.preventDefault();

  if (!startAction("delete", "Deleting loan by loan ID.")) {
    return;
  }

  const form = event.currentTarget;
  const data = new FormData(form);
  const loanId = data.get("loanId") || "";
  const status = getElement("deleted-loan-status");
  showFieldErrors("delete-loan-errors");

  try {
    const deletedLoan = await requestJson(
      `${loanApiPath}/${encodeURIComponent(loanId)}`,
      { method: "DELETE" }
    );
    renderSingleLoan("deleted-loan-result", deletedLoan);
    removeLoanFromVisibleResults(deletedLoan.loanId);
    await loadCurrentLoans();
    if (status) {
      status.textContent = `Deleted loan ${deletedLoan.loanId}.`;
    }
    showFeedback("success", `Deleted loan ${deletedLoan.loanId}.`);
  } catch (error) {
    const feedback = errorFeedback(error, "Loan could not be deleted.");
    showFieldErrors("delete-loan-errors", feedback.details);
    if (feedback.type === "not-found") {
      renderEmptyState("deleted-loan-result", "No loan exists for this loan ID.");
    }
    showFeedback(feedback.type, feedback.message, feedback.details);
    if (status) {
      status.textContent = feedback.message;
    }
  } finally {
    finishAction();
  }
}

function bindWebsiteEvents() {
  const createForm = getElement("create-loan-form");
  const refreshButton = getElement("current-loans-refresh");
  const borrowerSearchForm = getElement("borrower-search-form");
  const loanLookupForm = getElement("loan-lookup-form");
  const deleteLoanForm = getElement("delete-loan-form");

  document
    .querySelectorAll("[data-section-target]")
    .forEach((button) => {
      button.addEventListener("click", () => {
        showWorkflowSection(button.dataset.sectionTarget);
      });
    });

  if (createForm) {
    createForm.addEventListener("submit", handleCreateLoan);
  }

  if (refreshButton) {
    refreshButton.addEventListener("click", async () => {
      if (!startAction("list", "Refreshing current loans.")) {
        return;
      }

      try {
        await loadCurrentLoans({ announceSuccess: true });
      } finally {
        finishAction();
      }
    });
  }

  if (borrowerSearchForm) {
    borrowerSearchForm.addEventListener("submit", handleBorrowerSearch);
  }

  if (loanLookupForm) {
    loanLookupForm.addEventListener("submit", handleLoanLookup);
  }

  if (deleteLoanForm) {
    deleteLoanForm.addEventListener("submit", handleLoanDelete);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  bindWebsiteEvents();
  loadAuthStatus();
});
