

"use strict";

// Sweden Job Market Intelligence Dashboard

let allJobs = [];
let charts = {};

const $ = (id) => document.getElementById(id);

// Read CSV including quoted commas and line breaks
function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  text = text.replace(/^\uFEFF/, "");

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (char === '"') {
      if (quoted && text[i + 1] === '"') {
        field += '"';
        i++;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") {
        i++;
      }

      row.push(field);

      if (row.some(value => value.trim() !== "")) {
        rows.push(row);
      }

      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (quoted) {
    throw new Error("CSV contains an unclosed quoted field.");
  }

  row.push(field);

  if (row.some(value => value.trim() !== "")) {
    rows.push(row);
  }

  if (rows.length < 2) {
    throw new Error("CSV contains no job records.");
  }

  const headers = rows.shift().map(header =>
    header.trim().toLowerCase().replace(/[\s_-]+/g, "")
  );

  return rows.map(values => {
    const record = {};

    headers.forEach((header, index) => {
      record[header] = (values[index] || "").trim();
    });

    return record;
  });
}

// Support different CSV column names
function getField(record, names) {
  for (const name of names) {
    const key = name.toLowerCase()
      .replace(/[\s_-]+/g, "");

    if (record[key]) {
      return record[key];
    }
  }
  return "";
}

function normalizeJobs(records) {
  return records.map(record => ({
    id: getField(record, ["Job ID", "ID", "JobID"]),
    title: getField(record, [
      "Job Title", "Title", "Headline"
    ]),
    company: getField(record, [
      "Company", "Employer", "Company Name"
    ]) || "Unknown Company",
    city: getField(record, [
      "City", "Municipality", "Location"
    ]) || "Unknown City"
  })).filter(job => job.id || job.title);
}

// Status messages
function setStatus(message, isError = false) {
  $("status").textContent = message;
  $("status").classList.toggle("error", isError);
}

// Count values in any job field
function countBy(jobs, field) {
  const counts = new Map();

  jobs.forEach(job => {
    const value = job[field];

    if (!value || value.startsWith("Unknown ")) {
      return;
    }

    counts.set(value, (counts.get(value) || 0) + 1);
  });

  return [...counts.entries()].sort(
    (a, b) => b[1] - a[1] ||
      a[0].localeCompare(b[0])
  );
}

function uniqueCount(jobs, field) {
  return countBy(jobs, field).length;
}

// Load dataset into dashboard
function loadJobs(records, sourceName) {
  const jobs = normalizeJobs(records);

  if (jobs.length === 0) {
    throw new Error(
      "No job records found. Check your CSV headers."
    );
  }

  allJobs = jobs;

  $("dataLabel").textContent = sourceName;

  $("searchInput").value = "";
  $("cityFilter").value = "";
  $("companyFilter").value = "";

  updateFilterOptions();
  updateDashboard();

  setStatus(
    `Successfully loaded ${jobs.length} job listings from ${sourceName}.`
  );
}

// Update dropdowns
function fillSelect(elementId, values, label) {
  const select = $(elementId);

  select.replaceChildren();

  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = label;

  select.appendChild(defaultOption);

  values.forEach(([value]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function updateFilterOptions() {
  fillSelect(
    "cityFilter",
    countBy(allJobs, "city"),
    "All Cities"
  );

  fillSelect(
    "companyFilter",
    countBy(allJobs, "company"),
    "All Companies"
  );
}

// Filter data based on search and dropdowns
function getFilteredJobs() {
  const search = $("searchInput").value
    .toLowerCase().trim();

  const city = $("cityFilter").value;
  const company = $("companyFilter").value;

  return allJobs.filter(job => {
    const searchable = [
      job.id,
      job.title,
      job.company,
      job.city
    ].join(" ").toLowerCase();

    return (
      searchable.includes(search) &&
      (!city || job.city === city) &&
      (!company || job.company === company)
    );
  });
}

async function searchJobsFromAPI() {
  try {
    const keyword = document.getElementById("searchInput").value.trim();
    const city = document.getElementById("cityFilter").value;
    const company = document.getElementById("companyFilter").value;

    const params = new URLSearchParams({
      keyword: keyword,
      city: city,
      company: company
    });

    const response = await fetch(
      `/api/jobs/search?${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    document.getElementById("resultsCount").textContent =
      `${data.total_jobs} matching jobs`;

    if (!Array.isArray(data.jobs)) {
      throw new Error("Invalid API response");
    }

    const jobs = data.jobs.map(job => ({
      id: String(job.job_id ?? ""),
      title: job.job_title ?? "",
      company: job.company ?? "Unknown Company",
      city: job.city ?? "Unknown City"
    }));

    renderTable(jobs);
    renderCharts(jobs);

    document.getElementById("resultCount").textContent =
      `${jobs.length} matching jobs`;

  } catch (error) {
    console.error("Search failed:", error);
    setStatus("Unable to search jobs: " + error.message, true);
  }
}


// Update all dashboard elements
function updateDashboard() {
  const jobs = getFilteredJobs();

  $("totalJobs").textContent = jobs.length;
  $("totalCompanies").textContent =
    uniqueCount(jobs, "company");
  $("totalCities").textContent =
    uniqueCount(jobs, "city");
  $("totalRoles").textContent =
    uniqueCount(jobs, "title");

  $("resultCount").textContent =
    `${jobs.length} of ${allJobs.length} jobs`;

  renderTable(jobs);
  renderCharts(jobs);
}


async function showJobDetails(jobId) {
  const modal = document.getElementById("jobModal");
  const swedishButton = document.getElementById("showSwedish");
const englishButton = document.getElementById("showEnglish");

  // Clear previous job information
  document.getElementById("modalTitle").textContent =
    "Loading job details...";
  document.getElementById("modalCompany").textContent = "";
  document.getElementById("modalCity").textContent = "";
  document.getElementById("modalJobId").textContent = jobId;
  document.getElementById("modalDescription").textContent =
    "Loading description...";

  if (!modal.open) {
    modal.showModal();
  }

  try {
    const response = await fetch(
      `/api/jobs/${encodeURIComponent(jobId)}`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const job = await response.json();

    document.getElementById("modalTitle").textContent =
      job.job_title || "Untitled Job";

    document.getElementById("modalCompany").textContent =
      job.company || "Unknown Company";

    document.getElementById("modalCity").textContent =
      job.city || "Unknown City";

    document.getElementById("modalJobId").textContent =
      job.job_id;

    document.getElementById("modalDescription").textContent =
      job.job_description || "No description available.";
    
const originalDescription = job.job_description || "No description available.";

swedishButton.onclick = () => {
  document.getElementById("modalDescription").textContent =
    originalDescription;
};

englishButton.onclick = async () => {
  const descriptionElement =
    document.getElementById("modalDescription");

  descriptionElement.textContent = "Translating to English...";
  englishButton.disabled = true;

  try {
    const response = await fetch(
      `/api/jobs/${encodeURIComponent(jobId)}/translate`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    descriptionElement.textContent =
      data.english_description || "Translation unavailable.";

  } catch (error) {
    console.error("Translation error:", error);
    descriptionElement.textContent =
      "English translation unavailable. Please try again.";

  } finally {
    englishButton.disabled = false;
  }
};


  } catch (error) {
    console.error("Job details error:", error);

    document.getElementById("modalTitle").textContent =
      "Unable to load job details";

    document.getElementById("modalDescription").textContent =
      "Please try again.";
  }
}


// Render jobs table safely
function renderTable(jobs) {
  const tbody = $("jobsTable");
  tbody.replaceChildren();

  if (jobs.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");

    td.colSpan = 4;
    td.textContent = "No matching jobs found.";

    tr.appendChild(td);
    tbody.appendChild(tr);

    $("tableNote").textContent = "";
    return;
  }

  const maximumRows = 100;

  jobs.slice(0, maximumRows).forEach(job => {
    const tr = document.createElement("tr");

    [
      job.title || "Untitled",
      job.company,
      job.city,
      job.id || "N/A"
    ].forEach(value => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    });


    const actionCell = document.createElement("td");
    const detailsButton = document.createElement("button");

    detailsButton.textContent = "View Details";
    detailsButton.className = "details-btn";
    detailsButton.type = "button";
    detailsButton.disabled = !job.id;

    detailsButton.addEventListener("click", () => {
      showJobDetails(job.id);
    });

    actionCell.appendChild(detailsButton);
    tr.appendChild(actionCell);


    tbody.appendChild(tr);
  });

  $("tableNote").textContent =
    `Showing ${Math.min(jobs.length, maximumRows)} ` +
    `of ${jobs.length} matching records.`;
}

// Create or update charts
function createChart(canvasId, labels, values, color) {
  if (charts[canvasId]) {
    charts[canvasId].destroy();
    delete charts[canvasId];
  }

  if (typeof Chart === "undefined") {
    return;
  }

  const canvas = $(canvasId);

  if (!canvas) {
    return;
  }

  charts[canvasId] = new Chart(canvas, {
    type: "bar",

    data: {
      labels: labels,
      datasets: [{
        label: "Job Listings",
        data: values,
        backgroundColor: color,
        borderRadius: 5,
        maxBarThickness: 38
      }]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",

      plugins: {
        legend: {
          display: false
        },

        tooltip: {
          callbacks: {
            label: context =>
              `${context.parsed.x} job listings`
          }
        }
      },

      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          grid: {
            color: "#edf1f6"
          }
        },

        y: {
          grid: {
            display: false
          },
          ticks: {
            autoSkip: false
          }
        }
      }
    }
  });
}

function renderCharts(jobs) {
  const cities = countBy(jobs, "city").slice(0, 8);
  const companies = countBy(jobs, "company").slice(0, 8);
  const roles = countBy(jobs, "title").slice(0, 8);

  createChart(
    "cityChart",
    cities.map(item => item[0]),
    cities.map(item => item[1]),
    "#2563eb"
  );

  createChart(
    "companyChart",
    companies.map(item => item[0]),
    companies.map(item => item[1]),
    "#8b5cf6"
  );

  createChart(
    "roleChart",
    roles.map(item => item[0]),
    roles.map(item => item[1]),
    "#10b981"
  );
}

// File upload handler
async function handleUpload(event) {
  const file = event.target.files[0];

  if (!file) {
    return;
  }

  try {
    const csvText = await file.text();
    const records = parseCSV(csvText);

    loadJobs(records, file.name);

    if (typeof Chart === "undefined") {
      setStatus(
        "Data loaded, but Chart.js is unavailable. " +
        "Check your internet connection."
      );
    }
  } catch (error) {
    setStatus(`Upload failed: ${error.message}`, true);
  }

  event.target.value = "";
}

// Automatically load data exported by Python

async function loadDefaultCSV() {
  try {
    setStatus("Loading jobs from SQLite database...");

    const response = await fetch("/api/jobs");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!Array.isArray(data.jobs)) {
      throw new Error("Invalid API response");
    }

    const records = data.jobs.map(job => ({
      jobid: String(job.job_id ?? ""),
      jobtitle: job.job_title ?? "",
      company: job.company ?? "",
      city: job.city ?? ""
    }));

    loadJobs(records, "SQLite Database");
    document.getElementById("resultsCount").textContent =
      `${records.length} matching jobs`;

  } catch (error) {
    console.error(error);
    setStatus("Failed to load jobs: " + error.message, true);
  }
}


async function loadStatistics() {
  try {
    const response = await fetch("/api/stats");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const stats = await response.json();

    document.getElementById("totalJobs").textContent =
      stats.total_jobs;

    document.getElementById("totalCompanies").textContent =
      stats.total_companies;

    document.getElementById("totalCities").textContent =
      stats.total_cities;

    document.getElementById("totalRoles").textContent =
      stats.total_roles;

  } catch (error) {
    console.error("Failed to load statistics:", error);
  }
}


async function loadSkillsChart() {
  try {
    const response = await fetch("/api/skills");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    const topSkills = data.skills.slice(0, 10);

    createChart(
      "skillsChart",
      topSkills.map(skill => skill.skill_name),
      topSkills.map(skill => skill.job_count),
      "#f59e0b"
    );

  } catch (error) {
    console.error("Failed to load skills:", error);
  }
}


// Initialize page
document.addEventListener("DOMContentLoaded", () => {


async function loadLastUpdated() {
  try {
    const response = await fetch("/api/last-updated");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    const date = new Date(data.last_updated);

    document.getElementById("lastUpdated").textContent =
      "Last data collection: " +
      date.toLocaleString("en-SE", {
        timeZone: "Europe/Stockholm",
        dateStyle: "medium",
        timeStyle: "short"
      });

  } catch (error) {
    console.error("Failed to load timestamp:", error);

    document.getElementById("lastUpdated").textContent =
      "Last data collection: Unavailable";
  }
}


$("closeModal").addEventListener("click", () => {
  $("jobModal").close();
});

  $("csvFile").addEventListener("change", handleUpload);

  
$("searchInput").addEventListener(
  "input", searchJobsFromAPI
);

$("cityFilter").addEventListener(
  "change", searchJobsFromAPI
);

$("companyFilter").addEventListener(
  "change", searchJobsFromAPI
);


  $("clearFilters").addEventListener("click", () => {
    $("searchInput").value = "";
    $("cityFilter").value = "";
    $("companyFilter").value = "";

    searchJobsFromAPI();
  });

  loadDefaultCSV();
  loadStatistics();
  loadSkillsChart();
  loadLastUpdated();
});



document.getElementById("exportCSV").addEventListener("click", async () => {
  try {
    const keyword = document.getElementById("searchInput").value.trim();
    const city = document.getElementById("cityFilter").value;
    const company = document.getElementById("companyFilter").value;

    const params = new URLSearchParams({
      keyword: keyword,
      city: city,
      company: company
    });

    const response = await fetch(
      `/api/jobs/search?${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const jobs = data.jobs || [];

    if (jobs.length === 0) {
      alert("No matching jobs to export.");
      return;
    }

    const csvRows = [
      ["Job Title", "Company", "City", "Job ID"],
      ...jobs.map(job => [
        job.job_title,
        job.company,
        job.city,
        job.job_id
      ])
    ];

    const csv = csvRows.map(row =>
      row.map(value => {
        const text = String(value ?? "");
        return '"' + text.replace(/"/g, '""') + '"';
      }).join(",")
    ).join("\r\n");

    const blob = new Blob(
      ["\uFEFF" + csv],
      { type: "text/csv;charset=utf-8;" }
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "sweden_filtered_jobs.csv";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);

  } catch (error) {
    console.error("CSV export failed:", error);
    alert("Unable to export jobs.");
  }
});

