    function activity() {
        var activityDiv = document.getElementById("activitydiv");
        console.log(activityDiv);
        if (activityDiv.style.display === "block") {
            activityDiv.style.display = "none";
        } else {
            activityDiv.style.display = "block";
        }
    }

    $(document).ready(function () {
        $('.selectcountryfilter').select2();
    });
    window.addEventListener('load', function () {
        console.log("hello nisa")
        var currentUrl = window.location.pathname;
        console.log(currentUrl)
        var candidateButton = document.getElementById("candidate-button");
        var selectedButton = document.getElementById("selected-button");
        var placedcandidates = document.getElementById("placedcandidates");
        var rejectcandidates = document.getElementById("rejectcandidates");

        if (currentUrl === "/candidate") {
            candidateButton.style.backgroundColor = "#19355f";
            candidateButton.style.color = "#ffffff";
        }
        if (currentUrl === "/selecteddata") {
            selectedButton.style.backgroundColor = "#19355f";
            selectedButton.style.color = "#ffffff";
        }
        if (currentUrl === "/placedcandidates") {
            placedcandidates.style.backgroundColor = "#19355f";
            placedcandidates.style.color = "#ffffff";
        }
        if (currentUrl === "/rejectcandidates") {
            rejectcandidates.style.backgroundColor = "#19355f";
            rejectcandidates.style.color = "#ffffff";
        }

    });
    function showPdf(emailId) {
        markEmailAsRead(emailId);
        updateRowStatus(emailId, true);
        pdfWindow = window.open(`/pdf_content/${emailId}`);
        pdfWindow.addEventListener('beforeunload', () => {
            markEmailAsRead(emailId); // Call markEmailAsRead when PDF tab/window is closed
        });
    }

    function markEmailAsRead(emailId) {
        fetch(`/mark_as_read/${emailId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateRowStatus(emailId, true); // Update the row status
                    localStorage.setItem(`email_${emailId}`, 'true');
                }
            })
            .catch(error => {
                console.error('Error marking email as read:', error);
            });
    }

    function updateRowStatus(emailId, isRead) {
        const row = document.querySelector(`tr[data-email-id="${emailId}"]`);
        if (row) {
            row.classList.remove('unread', 'read');
            row.classList.add(isRead ? 'read' : 'unread');
        }
    }
    window.addEventListener('load', function () {
        const rows = document.querySelectorAll('.data-row');
        rows.forEach(row => {
            const emailId = row.getAttribute('data-email-id');
            const isRead = localStorage.getItem(`email_${emailId}`);
            if (isRead !== null) {
                updateRowStatus(emailId, isRead === 'true');
            }
        });
    });

    function handleSelectionChange(id, selectedOption) {
        console.log(selectedOption);
        if (selectedOption == 'Interested' || selectedOption == 'Reverse changes' || selectedOption == 'move to applied') {
            fetch('/updatemail', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id, selectedOption: selectedOption }), // Include the 'id' parameter here
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.message) {
                        if (selectedOption === 'Interested') {
                            window.location.href = "/selecteddata";
                        } else {
                            window.location.href = "/candidate";
                        }
                    }
                    console.log(data);
                })
                .catch((error) => {
                    // Handle errors if any
                    console.error('Error:', error);
                });
        } else {
            fetch('/deletemail', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id }), // Include the 'id' parameter here
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.message) {
                        window.location.href = "/candidate";
                    }
                    // Handle the response from the server if needed
                    console.log(data);
                })
                .catch((error) => {
                    // Handle errors if any
                    console.error('Error:', error);
                });
        }
    }



    function exportMore() {
        var exportDiv = document.getElementById("export");
        exportDiv.style.display = exportDiv.style.display === "none" ? "block" : "none";
        console.log("exportDiv.style.display = 'block'");
    };



    document.getElementById("searchKeyword").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        var year = $('#year_select').val();
        var country = $('#country_select').val();
        var subject = $('#subj_select').val();
        var prev_form = $('#prev_form').val();
        var source = $('#source').val();
        var keyword = this.value.trim();  // Get the search keyword

        sendAjaxRequest(year, country, subject, prev_form, source, keyword);
    }
});


//    function searchme() {
//        searchPdf();
//    }


//    function searchPdf() {
//        const keywordInput = document.getElementById("searchKeyword");
//        const loadingIndicator = document.getElementById("loadingIndicator");
//        var currentUrl = window.location.pathname.split('/').pop();
//
//
//        console.log("current_url", currentUrl)
//        if (!keywordInput || !loadingIndicator) {
//            console.error("Required elements not found in the DOM.");
//            return;
//        }
//
//        const keyword = keywordInput.value.trim();
//
//        if (keyword === "") {
//            console.error("Please enter a valid keyword.");
//            return;
//        }
//
//        loadingIndicator.style.display = "block";
//
//        fetch(`/search_pdf?keyword=${encodeURIComponent(keyword)}&currentUrl=${encodeURIComponent(currentUrl)}`)
//            .then(response => {
//                if (!response.ok) {
//                    throw new Error(`Request failed with status: ${response.status}`);
//                }
//                return response.json();
//            })
//            .then(data => {
//                loadingIndicator.style.display = "none";
//                console.log("Search Results:", data);
//                displaySearchResults(data);
//            })
//            .catch(error => {
//                loadingIndicator.style.display = "none";
//                console.error('Error:', error);
//            });
//    }


    function displaySearchResults(results) {
        const emailDataBody = document.getElementById("emailDataBody");
        emailDataBody.innerHTML = "";

        if (results.length === 0) {
            emailDataBody.innerHTML = "<tr><td colspan='6'>No matching PDFs found.</td></tr>";
        } else {
            results.forEach(email => {
                console.log("Email:", email);

                const actionColumn = `
                <td data-label="Action">
                    ${email.action === 'Interested' ? `

                        <a href="" data-toggle="tooltip" title="move back to applied candidates"
                           onclick="handleSelectionChange('${email.id}', 'move to applied')"><span class="select">Unselect</span></i></a>
                    ` : `
                        <a href="" data-toggle="tooltip" title="Select candidate" onclick="handleSelectionChange('${email.id}', 'Interested')">
                            <span class="select">Select</span>
                        </a>
                    `}
                </td>
            `;

                // Apply Jinja logic for email.status
                const statusColumn = `
<td data-label="Status">
    ${email.status !== 'Candidate Placement' && email.status !== 'Reject' && email.action != 'Interested' ? `
        ${email.status}
    ` : `
        ${email.status === 'Candidate Placement' && email.action == 'Interested' ? `
            Candidate placed
        ` : `
            ${email.status === 'Reject' && email.action == 'Interested' ? `
                Rejected
            ` : `
                ${email.status}
                <div class="cell-div"><input type="radio" id="resume_${email.id}" name="resume_${email.id}" value="resume" onclick="openUrl('/onereporting_form/${email.id}/resume')" ${email.status.trim().toLowerCase() === 'resume sent' ? 'checked' : ''}>
                <label for="resume">Resume</label></div>
                <div class="cell-div"><input type="radio" id="interview_${email.id}" name="interview_${email.id}" value="interview" onclick="openUrl('/onereporting_form/${email.id}/interview')" ${email.status.trim().toLowerCase() === 'interview scheduled' ? 'checked' : ''}>
                <label for="interview">Interview</label><br></div>
                <div class="cell-div"><input type="radio" id="placement_${email.id}" name="placement_${email.id}" value="placement" onclick="openUrl('/onereporting_form/${email.id}/placement')" ${email.status.trim().toLowerCase() === 'candidate placement' ? 'checked' : ''}>
                <label for="placement">Placement</label></div>
                <div class="cell-div"><input type="radio" id="help_${email.id}" name="help_${email.id}" value="help" onclick="openUrl('/onereporting_form/${email.id}/help')" ${email.status.trim().toLowerCase() === 'help another' ? 'checked' : ''}>
                <label for="help">Help Another</label></div>
                <div class="cell-div"><input type="radio" id="reject_${email.id}" name="reject_${email.id}" value="reject" onclick="openUrl('/onereporting_form/${email.id}/reject')" ${email.status.trim().toLowerCase() === 'reject' ? 'checked' : ''}>
                <label for="reject">Reject</label></div>
            `}
        `}
    `}
</td>





`;


                // Combine all columns into a table row
                const row = `
             <tr>
                 <td data-label="Applicant Info">
  <a href="/candidateprofile/${email.id}">
    <span style="text-decoration:underline">${email.sender_name}</span><br>
    ${email.email === 'No Email!' ? `<span style="color: red;">${email.email}</span>` : email.email} <br>
    ${email.phone_number ? (email.phone_number.length === 11 || email.phone_number.length === 10 || email.phone_number.length === 12 ? `<a href="tel:${email.phone_number}">${email.phone_number}</a>` : '-') : '-'}
  </a>
</td>

                  <td data-label="Job Detail">${email.subject_part2}<br>${email.subject_part1}</td>
                  <td data-label="Date">${email.formatted_date}</td>
                  <td data-label="Resumes">

                    ${email.file_content == null ? 'No PDF' : `<p style="cursor:pointer;padding-bottom:2px; border-bottom: 1px solid #19355f;" onclick="showPdf(${email.id}); return false;">View PDF</p>`}
                  </td>
                  ${statusColumn}
                  ${actionColumn}
              </tr>
          `;


                emailDataBody.innerHTML += row;
            });
        }
    }
    function openUrl(url) {
        window.location.href = url;
    }
$(document).ready(function () {
    var currentPage = 1;
    var itemsPerPage = 50;
    var totalFilteredPages = $('#total_pages').val(); // Retrieve total_pages value
    const loadingIndicator = document.getElementById("loadingIndicator");
    var keyword = '';

    // Debounce function to limit the rate at which the AJAX request is sent
    function debounce(func, delay) {
        let debounceTimer;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        }
    }

    function sendAjaxRequest(year, country, subject, prev_form, source, keyword) {
        debugger
        var currentUrl = window.location.href;
        var url = new URL(currentUrl);
        var currentUrl = window.location.href;
        var pathArray = currentUrl.split('/');
        var lastSegment = pathArray[pathArray.length - 1];
        var ajaxUrl = '/' + lastSegment;
        var ajaxUrl = '/' + lastSegment;
        url.searchParams.set('year_select', year);
        url.searchParams.set('country_select', country);
        url.searchParams.set('subj_select', subject);
        url.searchParams.set('prev_form', prev_form);
        url.searchParams.set('source', source);
        url.searchParams.set('keyword', keyword);

        console.log("Sending AJAX request to URL:", url.toString());
        loadingIndicator.style.display = "block";

        // Send AJAX request to server
        $.ajax({
            url: ajaxUrl,
            type: 'GET',
            data: {
                year_select: year,
                country_select: country,
                subj_select: subject,
                prev_form: prev_form,
                source: source,
                keyword: keyword,
                page: currentPage,
                per_page: itemsPerPage
            },
            success: function (response) {
                loadingIndicator.style.display = "none";

                // Update page with filtered data returned from server
                $('#filtered_data').html(response.html);
                var alldata = response.alldata;
                totalFilteredPages = response.total_pages; // Update totalFilteredPages based on the response

                // Display search results or perform other actions as needed
                console.log("Alldata:", alldata);
                displaySearchResults(alldata);

                // Update pagination links based on the totalFilteredPages
                updatePaginationLinks();
            },
            error: function (xhr, status, error) {
                loadingIndicator.style.display = "none";

                // Handle errors
                console.error(error);
            }
        });
    }

    // Function to update pagination links based on totalFilteredPages
    function updatePaginationLinks() {
        // Remove existing pagination links
        $('.pagination-list').empty();

        // Add pagination links for the totalFilteredPages
        var startPage = Math.max(currentPage - 2, 1);
        var endPage = Math.min(currentPage + 2, totalFilteredPages);

        // Add ellipsis if there are more pages before the start
        if (startPage > 1) {
            $('.pagination-list').append($('<li>').append($('<a>').attr('href', '#').attr('data-page', 1).text(1)));
            if (startPage > 2) {
                $('.pagination-list').append($('<li>').text('...'));
            }
        }

        // Add pages within the range
        for (var i = startPage; i <= endPage; i++) {
            var pageLink = $('<a>').attr('href', '#').attr('data-page', i).text(i);
            if (i === currentPage) {
                pageLink.css({
                    'font-weight': 'bold',
                    'background-color': '#19355f',
                    'color': 'white'
                });
            }
            $('.pagination-list').append($('<li>').append(pageLink));
        }

        // Add ellipsis if there are more pages after the end
        if (endPage < totalFilteredPages) {
            if (endPage < totalFilteredPages - 1) {
                $('.pagination-list').append($('<li>').text('...'));
            }
            $('.pagination-list').append($('<li>').append($('<a>').attr('href', '#').attr('data-page', totalFilteredPages).text(totalFilteredPages)));
        }
    }

    updatePaginationLinks();

    // Event listener for pagination controls
    $('.pagination').on('click', 'a', function () {
        currentPage = parseInt($(this).attr('data-page'));
        var year = $('#year_select').val();
        var country = $('#country_select').val();
        var subject = $('#subj_select').val();
        var prev_form = $('#prev_form').val();
        var source = $('#source').val();

        sendAjaxRequest(year, country, subject, prev_form, source, keyword);
    });

    // Event listener for filter dropdowns
    $('.selectcountryfilter').change(function () {
        // Get selected filter values
        var year = $('#year_select').val();
        var country = $('#country_select').val();
        var subject = $('#subj_select').val();
        var prev_form = $('#prev_form').val();
        var source = $('#source').val();
        console.log(year, country, subject, "hello");

        // Update data attributes of pagination links with current filter parameters
        $('.pagination a').each(function () {
            $(this).data('year', year);
            $(this).data('country', country);
            $(this).data('subject', subject);
            $(this).data('prev_form', prev_form);
            $(this).data('source', source);
        });

        // Send AJAX request to server with filter values
        sendAjaxRequest(year, country, subject, prev_form, source, keyword);
    });

    // Event listener for the search input
    $('#searchKeyword').on('keydown', function (e) {
        if (e.key === 'Enter') {
            keyword = $(this).val();
            var year = $('#year_select').val();
            var country = $('#country_select').val();
            var subject = $('#subj_select').val();
            var prev_form = $('#prev_form').val();
            var source = $('#source').val();
            sendAjaxRequest(year, country, subject, prev_form, source, keyword);
        }
    });

    // Debounce the search input for when user stops typing
    $('#searchKeyword').on('input', debounce(function () {
        keyword = $(this).val();
        var year = $('#year_select').val();
        var country = $('#country_select').val();
        var subject = $('#subj_select').val();
        var prev_form = $('#prev_form').val();
        var source = $('#source').val();
        sendAjaxRequest(year, country, subject, prev_form, source, keyword);
    }, 500)); // 500ms delay
});

