// --- static/js/report.js ---
document.addEventListener('DOMContentLoaded', function () {
    flatpickr("#fromDate", {
        enable: availableTransactionDates,
        dateFormat: "Y-m-d"
    });
    flatpickr("#toDate", {
        enable: availableTransactionDates,
        dateFormat: "Y-m-d"
    });



    const toggle = document.getElementById('bellToggle');
    const dropdown = document.getElementById('notificationDropdown');

    if (toggle && dropdown) {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            dropdown.classList.toggle('hidden');
        });
    }

    document.getElementById('filterForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const params = new URLSearchParams(new FormData(e.target));

        document.getElementById('exportBtn').href = `/report/export?${params.toString()}`;

        const url = `/report/data?${params.toString()}`;
        const res = await fetch(url);
        const data = await res.json();

        updateTable(data);
        updateChart(data);
        updatePieChart(data);

        // Show the share form if there is filtered data
        const shareSection = document.getElementById('shareSection');
        if (data.length > 0 && shareSection) {
            shareSection.classList.remove('hidden');
        } else if (shareSection) {
            shareSection.classList.add('hidden');
        }

        // Pre-fill the share form filter field
        document.getElementById('shareFiltersInput').value = JSON.stringify(Object.fromEntries(params));
    });

    function updateTable(data) {
        const tbody = document.querySelector("#reportTable tbody");
        tbody.innerHTML = "";

        if (data.length > 0) {
            document.getElementById('tableContainer').style.display = "block";
            document.getElementById('exportBtn').classList.remove("hidden");

            for (let txn of data) {
                const row = `<tr class="border-b hover:bg-gray-50">
                    <td class="px-4 py-2">${txn.date}</td>
                    <td class="px-4 py-2">${txn.description}</td>
                    <td class="px-4 py-2">${txn.amount}</td>
                    <td class="px-4 py-2">${txn.type}</td>
                    <td class="px-4 py-2">${txn.category}</td>
                </tr>`;
                tbody.insertAdjacentHTML('beforeend', row);
            }
        } else {
            document.getElementById('tableContainer').style.display = "none";
            document.getElementById('exportBtn').classList.add("hidden");
        }
    }

    const chartCtx = document.getElementById('reportChart').getContext('2d');
    let chartInstance = null;

    function updateChart(data) {
        document.getElementById('lineChartContainer').classList.toggle('hidden', data.length === 0);

        const labels = data.map(d => d.date);
        const amounts = data.map(d => d.amount);

        if (chartInstance) chartInstance.destroy();
        chartInstance = new Chart(chartCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Amount',
                    data: amounts,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.3,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Spending Trend' }
                }
            }
        });
    }

    let pieChartInstance = null;

    function updatePieChart(data) {
        const totalsByCategory = {};
    
        for (let txn of data) {
            if (txn.type === 'debit') {
                const cat = txn.category || 'Uncategorized';
                const amt = parseFloat(txn.amount);
                console.log("Txn type:", txn.type, "Cat:", cat, "Amt:", txn.amount, typeof txn.amount);
                if (!isNaN(amt)) {
                    totalsByCategory[cat] = (totalsByCategory[cat] || 0) + amt;
                }
            }
        }
    
        const hasPieData = Object.keys(totalsByCategory).length > 0;
        document.getElementById('pieChartContainer').classList.toggle('hidden', !hasPieData);
    
        const labels = Object.keys(totalsByCategory);
        const values = Object.values(totalsByCategory);
    
        console.log("Pie Labels:", labels);
        console.log("Pie Values:", values);
    
        if (pieChartInstance) pieChartInstance.destroy();
    
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        pieChartInstance = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56',
                        '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'right' },
                    title: { display: true, text: 'Spending by Category' }
                }
            }
        });
    }
    

    // Share functionality
    const shareForm = document.getElementById('shareForm');
    if (shareForm) {
        shareForm.addEventListener('submit', async function (e) {
            e.preventDefault();
    
            const username = document.getElementById('shareUserInput').value;
            const filters = document.getElementById('shareFiltersInput').value;
            const msgBox = document.getElementById('shareMessage');
    
            if (username.trim().toLowerCase() === currentUserEmail.toLowerCase()) {
                msgBox.textContent = "You cannot share data with yourself.";
                msgBox.className = 'text-red-600 mt-2';
                return;
            }
    
            const res = await fetch('/report/share', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, filters: JSON.parse(filters) })
            });
    
            const result = await res.json();
            if (result.status === 'success') {
                msgBox.textContent = result.message;
                msgBox.className = 'text-green-600 mt-2';
            } else {
                msgBox.textContent = result.error || 'Failed to share.';
                msgBox.className = 'text-red-600 mt-2';
            }
        });
    }
    
});

