ar selecteddataUrl = document.getElementById('selecteddata-url').value;
var candidatesUrl = document.getElementById('candidates-url').value;

 $(document).ready(function() {
            $("#country_select").change(function() {
                var selectedCountryCode = $("#country_select option:selected").val().trim();
                if (selectedCountryCode) {
                    console.log("Selected Country:", selectedCountryCode);
                    const loadingIndicator = document.getElementBy  Id("loadingIndicator");
                    loadingIndicator.style.display = "block";

                    // Send an AJAX request to the server to filter emails
                    $.ajax({
                        url: '/filter_emails',
                        type: 'GET',
                        data: { country_code: selectedCountryCode }, // Change to 'country_code'
                        success: function(data) {
                            loadingIndicator.style.display = "none";
                            console.log("Search Results:", data);

                            // Clear the existing table content
                            $('#emailDataBody').empty();

                            // Iterate through the filtered emails and append them to the table
                            data.forEach(function(email) {
                                const actionColumn = `
                                     <td data-label="Action">
                                          ${email.action === 'Interested' ? `
                                           <a href="" data-toggle="tooltip" title="Remove from Select" onclick="handleSelectionChange('${email.id}', 'Reverse changes')">
                                               <i style="font-size:20px;" class="fas fa-undo"></i>
                                           </a>
                                       ` : `
                                           <a href="" data-toggle="tooltip" title="Select candidate" onclick="handleSelectionChange('${email.id}', 'Interested')">
                                              <i style="font-size:20px; margin-right:8px;" class="fas fa-check-square"></i>
                                           </a>
                                       `}
                                     </td>
                                 `;

                                  const newRow = `
                                     <tr>
                                         <td>${email.sender_name}<br>${email.email}<br><a href="tel:${email.phone_number}">${email.phone_number}</a></td>
                                         <td>${email.subject_part2}<br>${email.subject_part1}</td>
                                         <td>${email.formatted_date}</td>
                                         <td data-label="Resumes">
                                             <a href="#" style="padding-bottom:2px; border-bottom: 1px solid #19355f;" onclick="showPdf('${email.id}'); return false;">View PDF</a>
                                         </td>
                                         <td data-label="Current Status">${email.status}</td>
                                         ${actionColumn}
                                         <!-- Add more columns as needed -->
                                     </tr>
                                  `;

                                 $('#emailDataBody').append(newRow);
                              });

                        },
                        error: function(error) {
                            console.error("AJAX Error:", error);
                        }
                    });
                }
            });
 });
//candidateChart

console.log(dataFromServer.interviews,"dataFromServer.interviews")
console.log(dataFromServer.resumesents,"dataFromServer.resumesents")
console.log(dataFromServer.helpings,"dataFromServer.helpings")


function filterDataByDate(dataArray, key) {
  const today = new Date().toISOString().slice(0, 10);
  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === today);
}
const interviewstodayData = filterDataByDate(dataFromServer.interviews, 'interviews');
const resumesentstodayData = filterDataByDate(dataFromServer.resumesents, 'resumesents');
const helpingstodayData = filterDataByDate(dataFromServer.helpings, 'helpings');
function filterDataByYesterday(dataArray, key) {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayFormatted = yesterday.toISOString().slice(0, 10);

  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === yesterdayFormatted);
}
const interviewsyesterdayData = filterDataByYesterday(dataFromServer.interviews, 'interviews');
const resumesentsyesterdayData = filterDataByYesterday(dataFromServer.resumesents, 'resumesents');
const helpingsyesterdayData = filterDataByYesterday(dataFromServer.helpings, 'helpings');

function filterDataByLastNDays(dataArray, key, n) {
  const currentDate = new Date();
  const filteredData = [];

  for (let i = 0; i <= n; i++) {
    const day = new Date(currentDate);
    day.setDate(currentDate.getDate() - i);
    const dayFormatted = day.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}
const daysToFilter = 3;
const interviewsLast3DaysData = filterDataByLastNDays(dataFromServer.interviews, 'interviews', daysToFilter);
const resumesentsLast3DaysData = filterDataByLastNDays(dataFromServer.resumesents, 'resumesents', daysToFilter);
const helpingsLast3DaysData = filterDataByLastNDays(dataFromServer.helpings, 'helpings', daysToFilter);

const dateFilterDropdown = document.getElementById("dateFilterforcan");
dateFilterDropdown.addEventListener("change", handleDateFilter);
const customDateFormforcan = document.getElementById("customDateFormforcan");
customDateFormforcan.addEventListener("submit", handleCustomDateFilter);
const usernameFilterDropdown = document.getElementById("selectUsernamefor");
usernameFilterDropdown.addEventListener("change", handleUsernameFilter);

const interviewData = dataFromServer.interviews;
const resumesentData = dataFromServer.resumesents;
const helpingData = dataFromServer.helpings;


const sumCountsByUsername = (dataArray) => {
  const result = {};
  dataArray.forEach(item => {
    const { user_name, count } = item;
    result[user_name] = (result[user_name] || 0) + parseInt(count);
  });
  return result;
};



const interviewsSummedData = sumCountsByUsername(interviewData);
const resumesentsSummedData = sumCountsByUsername(resumesentData);
const helpingsSummedData = sumCountsByUsername(helpingData);

var candidatectx = document.getElementById("candidateChart").getContext("2d");
var myChartcandidate = new Chart(candidatectx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "Helping",
        backgroundColor: '#4d0202',
        hoverBackgroundColor: '#4d0202',
        borderColor: '#4d0202',
        data: dataFromServer.usernames.map(username => helpingsSummedData[username] || 0),
        barPercentage: 0.3,
      },
      {
        label: "Resume Sents",
        backgroundColor: '#4e8757',
        hoverBackgroundColor: '#4e8757',
        borderColor: '#4e8757',
        data: dataFromServer.usernames.map(username => resumesentsSummedData[username] || 0),
        barPercentage: 0.3,
      },
      {
        label: "Interviews",
        backgroundColor: '#9ea60d',
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
        data: dataFromServer.usernames.map(username => interviewsSummedData[username] || 0),
        barPercentage: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    scales: {

      xAxes: [

        {
        ticks: {
          maxRotation: 90, // Adjust the rotation angle as needed
          minRotation: 10,
        },
        gridLines: {
          display: false, // Remove the grid lines
        },
          barPercentage: 0.7, // Adjust the bar width as needed
        categoryPercentage: 0.6,

        },
      ],
    },
   plugins: {
      labels: false, // Disable rendering labels
    },

  },
});
function filterDataByCustomRange(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}
function filterDataByUsername(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}
function updateChartcandi(helpingData, resumesentData, interviewsData) {
  const usernames = dataFromServer.usernames;
  const datasetCount = usernames.length;

  const helpingCounts = new Array(datasetCount).fill(0);
  const resumesentCounts = new Array(datasetCount).fill(0);
  const interviewsCounts = new Array(datasetCount).fill(0);

  // Check if the input data is an array
  if (Array.isArray(helpingData)) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      const helpingItem = helpingData.find(item => item.user_name === username);
      const resumesentItem = resumesentData.find(item => item.user_name === username);
      const interviewsItem = interviewsData.find(item => item.user_name === username);

      helpingCounts[i] = helpingItem ? parseInt(helpingItem.count) : 0;
      resumesentCounts[i] = resumesentItem ? parseInt(resumesentItem.count) : 0;
      interviewsCounts[i] = interviewsItem ? parseInt(interviewsItem.count) : 0;
    }
  } else if (typeof helpingData === 'object' && helpingData !== null) {
    // If it's an object, extract values from the object
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      helpingCounts[i] = parseInt(helpingData[username]) || 0;
      resumesentCounts[i] = parseInt(resumesentData[username]) || 0;
      interviewsCounts[i] = parseInt(interviewsData[username]) || 0;
    }
  }

  myChartcandidate.data.datasets[0].data = helpingCounts;
  myChartcandidate.data.datasets[1].data = resumesentCounts;
  myChartcandidate.data.datasets[2].data = interviewsCounts;
  myChartcandidate.update();
}


function handleDateFilter() {
  const selectedValue = dateFilterDropdown.value;
  customDateFormforcan.style.display = 'none';

  if (selectedValue === "select1") {
    // Check if the summed data is available before updating the chart
    if (helpingsSummedData && resumesentsSummedData && interviewsSummedData) {
      updateChartcandi(helpingsSummedData, resumesentsSummedData, interviewsSummedData);
//      print(updateChartcandi,"updateChartcandi")
    }
  } else if (selectedValue === "all1") {
    updateChartcandi(helpingstodayData, resumesentstodayData, interviewstodayData);
  } else if (selectedValue === "yesterday1") {
    updateChartcandi(helpingsyesterdayData, resumesentsyesterdayData, interviewsyesterdayData);
  } else if (selectedValue === "last3days1") {
    updateChartcandi(helpingsLast3DaysData, resumesentsLast3DaysData, interviewsLast3DaysData);
  } else if (selectedValue === "custom1") {
    customDateFormforcan.style.display = 'block';
  } else {
    updateChartcandi(helpingsSummedData, resumesentsSummedData, interviewsSummedData);
  }
}



function handleCustomDateFilter(event) {
  customDateFormforcan.style.display = 'none';
  event.preventDefault();
  const startDate = document.getElementById("startDate1").value;
  const endDate = document.getElementById("endDate1").value;

  const customInterviewsData = filterDataByCustomRange(dataFromServer.interviews, startDate, endDate);
  const customHelpingData = filterDataByCustomRange(dataFromServer.helpings, startDate, endDate);
  const customResumesentData = filterDataByCustomRange(dataFromServer.resumesents, startDate, endDate);

  updateChartcandi(customHelpingData, customResumesentData,customInterviewsData);
}
function handleUsernameFilter(event) {
debugger
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterDropdown.value;

  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday1") {
      updateChartcandi(helpingsyesterdayData, resumesentsyesterdayData, interviewsyesterdayData);
    } else if (selectedDateFilter === "last3days1") {
      updateChartcandi(helpingsLast3DaysData, resumesentsLast3DaysData, interviewsLast3DaysData);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;
        const customInterviewsData = filterDataByCustomRange(dataFromServer.interviews, startDate, endDate);
        const customHelpingData = filterDataByCustomRange(dataFromServer.helpings, startDate, endDate);
        const customResumesentData = filterDataByCustomRange(dataFromServer.resumesents, startDate, endDate);
      updateChartcandi(customHelpingData, customResumesentData,customInterviewsData, );
    }  else if (selectedDateFilter === "allcustom1") {
      updateChartcandi(helpingstodayData, resumesentstodayData, interviewstodayData);
    }
    else {
      updateChartcandi(helpingsSummedData, resumesentsSummedData, interviewsSummedData);
    }
  } else {
    if (selectedDateFilter === "yesterday1") {
      var userDataYesterday = helpingsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesentsYesterday = resumesentsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataInterviewsYesterday = interviewsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi( userDataYesterday, userDataResumesentsYesterday,userDataInterviewsYesterday);
    } else if (selectedDateFilter === "last3days1") {
      var userDataLast3Days = helpingsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesentsLast3Days = resumesentsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataInterviewsLast3Days = interviewsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi( userDataLast3Days, userDataResumesentsLast3Days,userDataInterviewsLast3Days);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;
      var customUserData = dataFromServer.helpings.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataResumesents = dataFromServer.resumesents.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataInterviews = dataFromServer.interviews.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartcandi( customUserData,customUserDataResumesents,customUserDataInterviews, );
    } else if (selectedDateFilter === "allcustom1") {
      var userDataInterviews  = interviewstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userData= helpingstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesents  = resumesentstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi(userData,userDataResumesents, userDataInterviews);
    }else  {
      var userDataInterviews  = interviewsSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userData= helpingsSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesents  = resumesentsSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi(userData,userDataResumesents, userDataInterviews);
    }
  }
}





//placementChart
console.log(dataFromServer.candidat
