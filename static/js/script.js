
// ======================================================
// 1. DOM ELEMENTS
// ======================================================

const form = document.getElementById("predictionForm");
const predictBtn = document.getElementById("predictBtn");
const errorMessage = document.getElementById("errorMessage");

const emptyResult = document.getElementById("emptyResult");
const predictionResult = document.getElementById("predictionResult");

const historyBody = document.getElementById("historyBody");
const refreshHistoryBtn = document.getElementById("refreshHistory");

const historySearch = document.getElementById("historySearch");
const gradeFilter = document.getElementById("gradeFilter");

const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const themeText = document.getElementById("themeText");


// ======================================================
// 2. GLOBAL VARIABLES
// ======================================================

let historyRecords = [];

let gradeChartInstance = null;
let scoreChartInstance = null;

let gradeChartData = null;
let scoreChartData = null;


// ======================================================
// 3. HELPER FUNCTIONS
// ======================================================

// Safely convert values into numbers
function formatNumber(value, decimals = 2) {
    const number = Number(value);

    return Number.isFinite(number)
        ? number.toFixed(decimals)
        : "0.00";
}


// Fetch JSON response
async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }

    return data;
}


// ======================================================
// 4. STUDENT PERFORMANCE PREDICTION
// ======================================================

if (form) {
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        errorMessage.textContent = "";

        const studentData = {
            age: Number(document.getElementById("age").value),

            attendance_percentage: Number(
                document.getElementById("attendance_percentage").value
            ),

            study_hours_per_week: Number(
                document.getElementById("study_hours_per_week").value
            ),

            previous_grade: Number(
                document.getElementById("previous_grade").value
            ),

            assignments_total: Number(
                document.getElementById("assignments_total").value
            ),

            assignments_completed: Number(
                document.getElementById("assignments_completed").value
            ),

            internal_marks: Number(
                document.getElementById("internal_marks").value
            ),

            quiz_average: Number(
                document.getElementById("quiz_average").value
            ),

            class_participation_score: Number(
                document.getElementById("class_participation_score").value
            )
        };


        // Loading state
        predictBtn.disabled = true;
        predictBtn.textContent = "Predicting...";


        try {

            const result = await fetchJSON("/api/predict", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(studentData)
            });


            // Display predicted score
            document.getElementById("predictedScore").textContent =
                formatNumber(result.predicted_score);


            // Display predicted grade
            document.getElementById("predictedGrade").textContent =
                result.predicted_grade;


            // Display prediction ID
            document.getElementById("predictionId").textContent =
                "Prediction ID: " + result.prediction_id;


            // Switch result sections
            emptyResult.classList.add("hidden");
            predictionResult.classList.remove("hidden");


            // Refresh dashboard data
            await Promise.all([
                loadHistory(),
                loadAnalytics()
            ]);


        } catch (error) {

            errorMessage.textContent = error.message;

            console.error("Prediction error:", error);

        } finally {

            predictBtn.disabled = false;

            predictBtn.textContent =
                "Predict Student Performance →";
        }
    });
}


// ======================================================
// 5. PREDICTION HISTORY
// ======================================================

async function loadHistory() {

    historyBody.innerHTML =
        '<tr><td colspan="7">Loading history...</td></tr>';

    try {

        const result = await fetchJSON("/api/history");

        historyRecords = Array.isArray(result.records)
            ? result.records
            : [];


        // Apply search and filter
        renderHistory();

        // Update student insights
        renderStudentInsights();  


    } catch (error) {

        historyBody.innerHTML =
            '<tr><td colspan="7">Unable to load prediction history.</td></tr>';

        console.error("History error:", error);
    }
}


// Render history table
function renderHistory() {

    const searchTerm = historySearch
        ? historySearch.value.trim().toLowerCase()
        : "";

    const selectedGrade = gradeFilter
        ? gradeFilter.value
        : "all";

    
    // Filter history records

    const isIdSearch = /^(id\s*|#)?\d+$/i.test(searchTerm);

    const normalizedSearch = searchTerm
        .replace(/^(id\s*|#)/i, "")
        .trim();

    const filteredRecords = historyRecords.filter(record => {

        const studentId = String(record.id);

        const searchableText = [
            record.age,
            record.attendance_percentage,
            record.study_hours_per_week,
            record.predicted_score,
            record.predicted_grade,
            record.created_at
        ].join(" ").toLowerCase();


        // Exact ID search
        const matchesSearch = isIdSearch
            ? studentId === normalizedSearch
            : searchableText.includes(searchTerm);


        // Grade filter
        const matchesGrade =
            !selectedGrade ||
            selectedGrade.toLowerCase() === "all" ||
            String(record.predicted_grade).toLowerCase() ===
            selectedGrade.toLowerCase();


        return matchesSearch && matchesGrade;
    });




    // No records available
    if (filteredRecords.length === 0) {

        historyBody.innerHTML =
            '<tr><td colspan="7">No matching prediction records found.</td></tr>';

        return;
    }


    // Clear previous table rows
    historyBody.innerHTML = "";


    filteredRecords.forEach(record => {

        const row = document.createElement("tr");


        const values = [
            record.id ?? record.prediction_id,
            record.age,
            formatNumber(record.attendance_percentage, 1) + "%",
            formatNumber(record.study_hours_per_week, 1),
            formatNumber(record.predicted_score),
            record.predicted_grade,
            record.created_at
        ];


        values.forEach(value => {

            const cell = document.createElement("td");

            cell.textContent =
                value === null || value === undefined ? "-" : value;

            row.appendChild(cell);
        });


        historyBody.appendChild(row);
    });
}


// ======================================================
// STUDENT INSIGHTS
// ======================================================

function renderStudentInsights() {

    const totalElement = document.getElementById("insightsTotal");
    const attendanceElement = document.getElementById("insightsAttendance");
    const studyHoursElement = document.getElementById("insightsStudyHours");
    const attentionElement = document.getElementById("insightsAttention");
    const container = document.getElementById("insightsContainer");

    if (
        !totalElement ||
        !attendanceElement ||
        !studyHoursElement ||
        !attentionElement ||
        !container
    ) {
        return;
    }

    // Handle empty history
    if (historyRecords.length === 0) {

        totalElement.textContent = "0";
        attendanceElement.textContent = "0%";
        studyHoursElement.textContent = "0";
        attentionElement.textContent = "0";

        container.innerHTML =
            "<p>No prediction records available yet. Generate a prediction to see student insights.</p>";

        return;
    }

    // Calculate averages
    let attendanceTotal = 0;
    let attendanceCount = 0;

    let studyHoursTotal = 0;
    let studyHoursCount = 0;

    let attentionCount = 0;

    historyRecords.forEach(record => {

        const attendance = Number(record.attendance_percentage);
        const studyHours = Number(record.study_hours_per_week);

        const totalAssignments = Number(record.assignments_total);
        const completedAssignments = Number(record.assignments_completed);

        if (Number.isFinite(attendance)) {
            attendanceTotal += attendance;
            attendanceCount++;
        }

        if (Number.isFinite(studyHours)) {
            studyHoursTotal += studyHours;
            studyHoursCount++;
        }

        // Rule-based review indicators
        const lowAttendance =
            Number.isFinite(attendance) && attendance < 75;

        const validAssignmentData =
            Number.isFinite(totalAssignments) &&
            Number.isFinite(completedAssignments) &&
            totalAssignments > 0;

        const lowAssignmentCompletion = validAssignmentData &&
            (completedAssignments / totalAssignments) < 0.70;

        if (lowAttendance || lowAssignmentCompletion) {
            attentionCount++;
        }
    });

    const averageAttendance = attendanceCount > 0
        ? attendanceTotal / attendanceCount
        : 0;

    const averageStudyHours = studyHoursCount > 0
        ? studyHoursTotal / studyHoursCount
        : 0;

    // Update insight cards
    totalElement.textContent = historyRecords.length;

    attendanceElement.textContent =
        formatNumber(averageAttendance, 1) + "%";

    studyHoursElement.textContent =
        formatNumber(averageStudyHours, 1);

    attentionElement.textContent = attentionCount;

    // Generate observations
    let insightsHTML = `
        <h3>Overall Academic Overview</h3>
        <p>
            The database currently contains
            <strong>${historyRecords.length}</strong>
            prediction records.
        </p>
        <p>
            Average attendance is
            <strong>${formatNumber(averageAttendance, 1)}%</strong>,
            while average weekly study time is
            <strong>${formatNumber(averageStudyHours, 1)} hours</strong>.
        </p>
    `;

    insightsHTML += `
        <h3>Records Requiring Review</h3>
        <p>
            <strong>${attentionCount}</strong> prediction records
            meet at least one of the review indicators.
        </p>
        <ul>
            <li>Attendance below 75%.</li>
            <li>Assignment completion below 70%, when total assignments are greater than zero.</li>
        </ul>
        <p>
            These are simple rule-based indicators for further review.
            They are not AI diagnoses or predictions of academic failure.
        </p>
    `;

    container.innerHTML = insightsHTML;
}


// Search history
if (historySearch) {

    historySearch.addEventListener("input", renderHistory);
}


// Filter history by grade
if (gradeFilter) {

    gradeFilter.addEventListener("change", renderHistory);
}


// Refresh history
if (refreshHistoryBtn) {

    refreshHistoryBtn.addEventListener("click", loadHistory);
}


// ======================================================
// 6. ANALYTICS DASHBOARD
// ======================================================

async function loadAnalytics() {

    try {

        // Fetch analytics from Flask
        const data = await fetchJSON("/api/analytics");


        // Update analytics cards
        document.getElementById("totalPredictions").textContent =
            data.total_predictions ?? 0;


        document.getElementById("averageScore").textContent =
            formatNumber(data.average_score);


        const distribution = data.grade_distribution || {};


        document.getElementById("gradeA").textContent =
            distribution["A"] || 0;


        document.getElementById("gradeO").textContent =
            distribution["O"] || 0;


        // Prepare grade chart data
        gradeChartData = {
            labels: Object.keys(distribution),

            datasets: [{
                data: Object.values(distribution),

                backgroundColor: [
                    "#5b50e8",
                    "#3182ce",
                    "#159b69",
                    "#f59e0b",
                    "#ef6b75",
                    "#8b5cf6",
                    "#64748b"
                ],

                borderWidth: 0,

                hoverOffset: 8
            }]
        };


        // Fetch prediction history for score chart
        const historyData = await fetchJSON("/api/history");

        const records = Array.isArray(historyData.records)
            ? [...historyData.records].reverse()
            : [];


        scoreChartData = {
            labels: records.map(record => "ID " + record.id),

            datasets: [{
                label: "Predicted Score",

                data: records.map(record =>
                    Number(record.predicted_score)
                ),

                backgroundColor: "#6558e9",

                borderRadius: 7,

                maxBarThickness: 45
            }]
        };


        // Draw charts
        renderCharts();


    } catch (error) {

        console.error("Analytics error:", error);
    }
}


// ======================================================
// MODEL PERFORMANCE
// ======================================================

async function loadModelPerformance() {

    try {

        const data = await fetchJSON("/api/model-performance");

        const metadata = data.model_performance;

        if (!metadata) {
            throw new Error("Model metadata not found");
        }

        const regression = metadata.regression_model;
        const classification = metadata.classification_model;

        function updateText(id, value) {
            const element = document.getElementById(id);

            if (element) {
                element.textContent = value;
            }
        }

        // Regression metrics
        updateText("modelMAE", Number(regression.MAE).toFixed(4));
        updateText("modelRMSE", Number(regression.RMSE).toFixed(4));
        updateText("modelR2", Number(regression.R2).toFixed(4));

        // Classification metrics
        updateText(
            "modelAccuracy",
            (Number(classification.accuracy) * 100).toFixed(2) + "%"
        );

        updateText(
            "modelMacroF1",
            Number(classification.macro_f1).toFixed(4)
        );

        updateText(
            "modelBalancedAccuracy",
            (Number(classification.balanced_accuracy) * 100).toFixed(2) + "%"
        );

        // Dataset split
        updateText("trainingRecords", metadata.training_records);
        updateText("testingRecords", metadata.testing_records);

        // Regression details
        updateText("regressionName", regression.name);
        updateText("regressionTarget", regression.target);
        updateText("regressionMAE", Number(regression.MAE).toFixed(4));
        updateText("regressionRMSE", Number(regression.RMSE).toFixed(4));
        updateText("regressionR2", Number(regression.R2).toFixed(4));

        // Classification details
        updateText("classificationName", classification.name);
        updateText("classificationTarget", classification.target);

        updateText(
            "classificationAccuracy",
            (Number(classification.accuracy) * 100).toFixed(2) + "%"
        );

        updateText(
            "classificationMacroF1",
            Number(classification.macro_f1).toFixed(4)
        );

        updateText(
            "classificationBalancedAccuracy",
            (Number(classification.balanced_accuracy) * 100).toFixed(2) + "%"
        );

        console.log("Model performance loaded successfully!");

    } catch (error) {

        console.error("Model performance error:", error);

    }
}



// ======================================================
// 7. CHART RENDERING
// ======================================================

function renderCharts() {

    if (typeof Chart === "undefined") {

        console.error("Chart.js library is not loaded.");

        return;
    }


    const gradeCanvas = document.getElementById("gradeChart");
    const scoreCanvas = document.getElementById("scoreChart");


    if (!gradeCanvas || !scoreCanvas) {
        return;
    }


    const isDark =
        document.documentElement.getAttribute("data-theme") === "dark";


    const textColor = isDark ? "#e2e8f0" : "#475569";

    const gridColor = isDark
        ? "rgba(255,255,255,0.10)"
        : "rgba(0,0,0,0.08)";


    // Destroy previous charts
    if (gradeChartInstance) {
        gradeChartInstance.destroy();
    }

    if (scoreChartInstance) {
        scoreChartInstance.destroy();
    }


    // Grade distribution doughnut chart
    gradeChartInstance = new Chart(gradeCanvas, {

        type: "doughnut",

        data: gradeChartData || {
            labels: [],
            datasets: [{ data: [] }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "68%",

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: textColor,

                        usePointStyle: true,

                        padding: 18,

                        font: {
                            family: "Inter",
                            size: 11
                        }
                    }
                }
            }
        }
    });


    // Predicted score bar chart
    scoreChartInstance = new Chart(scoreCanvas, {

        type: "bar",

        data: scoreChartData || {
            labels: [],
            datasets: [{ data: [] }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                x: {

                    ticks: {
                        color: textColor
                    },

                    grid: {
                        color: gridColor
                    }
                },

                y: {

                    beginAtZero: true,

                    max: 100,

                    ticks: {

                        stepSize: 20,

                        color: textColor
                    },

                    grid: {
                        color: gridColor
                    }
                }
            },

            plugins: {

                legend: {
                    display: false
                }
            }
        }
    });
}


// ======================================================
// 8. LIGHT MODE / DARK MODE
// ======================================================

function applyTheme(theme) {

    const isDark = theme === "dark";


    // Update HTML theme
    document.documentElement.setAttribute(
        "data-theme",
        theme
    );


    // Update theme button
    if (themeIcon) {

        themeIcon.textContent = isDark ? "☀" : "☾";
    }


    if (themeText) {

        themeText.textContent =
            isDark ? "Light Mode" : "Dark Mode";
    }


    if (themeToggle) {

        themeToggle.setAttribute(
            "aria-label",
            isDark ? "Switch to light mode" : "Switch to dark mode"
        );
    }


    // Save user preference
    try {

        localStorage.setItem("studentDashboardTheme", theme);

    } catch (error) {

        console.warn("Unable to save theme preference:", error);
    }


    // Update chart colors
    if (gradeChartData && scoreChartData) {

        renderCharts();
    }
}


// Load saved theme
function initializeTheme() {

    let savedTheme = "light";

    try {

        savedTheme =
            localStorage.getItem("studentDashboardTheme") || "light";

    } catch (error) {

        console.warn("Unable to read saved theme:", error);
    }


    if (savedTheme !== "dark" && savedTheme !== "light") {

        savedTheme = "light";
    }


    applyTheme(savedTheme);
}


// Toggle theme
if (themeToggle) {

    themeToggle.addEventListener("click", function () {

        const currentTheme =
            document.documentElement.getAttribute("data-theme") || "light";


        const newTheme =
            currentTheme === "light" ? "dark" : "light";


        applyTheme(newTheme);
    });
}


// ======================================================
// 9. INITIALIZE DASHBOARD
// ======================================================

// Set saved theme
initializeTheme();


// Load initial dashboard data
loadHistory();

loadAnalytics();

loadModelPerformance();


// ======================================================
// 10. SIDEBAR NAVIGATION ACTIVE STATE
// ======================================================

const navLinks = document.querySelectorAll(".sidebar-nav a");

navLinks.forEach(link => {

    link.addEventListener("click", function () {

        // Remove active class from all links
        navLinks.forEach(navLink => {
            navLink.classList.remove("active");
        });

        // Add active class to clicked link
        this.classList.add("active");
    });

});
