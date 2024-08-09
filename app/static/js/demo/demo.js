type = ['primary', 'info', 'success', 'warning', 'danger'];

demo = {
  initPickColor: function() {
    $('.pick-class-label').click(function() {
      var new_class = $(this).attr('new-class');
      var old_class = $('#display-buttons').attr('data-class');
      var display_div = $('#display-buttons');
      if (display_div.length) {
        var display_buttons = display_div.find('.btn');
        display_buttons.removeClass(old_class);
        display_buttons.addClass(new_class);
        display_div.attr('data-class', new_class);
      }
    });
  },
  initDocChart: function() {
    chartColor = "#FFFFFF";
  },
  initDashboardPageCharts: function() {

//DealChart

//console.log(dataFromServer.reopendeals,"dataFromServer.reopendeals")
//console.log(dataFromServer.contractnotsigned,"dataFromServer.contractnotsigned")
//console.log(dataFromServer.contractsigned,"dataFromServer.contractsigned")

function filterDataByCurrentWeek(dataArray, key) {
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay()); // Start of current week
  const startOfWeekFormatted = startOfWeek.toISOString().slice(0, 10);

  return dataArray.filter(item => {
    const itemDate = new Date(item.date.replace(/[\s,]+/g, '-'));
    return itemDate >= startOfWeek;
  });
}


const reopendealsyesterdayData = filterDataByCurrentWeek(dataFromServer.reopendeals, 'reopendeals');
const contractnotsignedyesterdayData = filterDataByCurrentWeek(dataFromServer.contractnotsigned, 'contractnotsigned');
const contractsignedyesterdayData = filterDataByCurrentWeek(dataFromServer.contractsigned, 'contractsigned');

function filterDataByLastWeek(dataArray, key) {
  const today = new Date();
  const endOfWeek = new Date(today);
  endOfWeek.setDate(today.getDate() - today.getDay()); // End of current week
  const startOfWeek = new Date(endOfWeek);
  startOfWeek.setDate(endOfWeek.getDate() - 6); // Start of last week

  const startOfWeekFormatted = startOfWeek.toISOString().slice(0, 10);
  const endOfWeekFormatted = endOfWeek.toISOString().slice(0, 10);

  return dataArray.filter(item => {
    const itemDate = new Date(item.date.replace(/[\s,]+/g, '-'));
    return itemDate >= startOfWeek && itemDate <= endOfWeek;
  });
}


const reopendealsLast3DaysData = filterDataByLastWeek(dataFromServer.reopendeals, 'reopendeals');
const contractnotsignedLast3DaysData = filterDataByLastWeek(dataFromServer.contractnotsigned, 'contractnotsigned');
const contractsignedLast3DaysData = filterDataByLastWeek(dataFromServer.contractsigned, 'contractsigned');

const dateFilterdealDropdown = document.getElementById("dateFilterfordeal");
dateFilterdealDropdown.addEventListener("change", handleDateFilterdeal);

const customDateFormfordeal = document.getElementById("customDateFormfordeal");
customDateFormfordeal.addEventListener("submit", handleCustomDateFilterdeal);

const usernameFilterdealDropdown = document.getElementById("selectUsernamefordeal");
usernameFilterdealDropdown.addEventListener("change", handleUsernameFilterdeal);

//const reopendealsData = dataFromServer.reopendeals;
//const contractnotsignedData = dataFromServer.contractnotsigned;
//const contractsignedData = dataFromServer.contractsigned;

const reopendealsData = reopendealsyesterdayData;
const contractnotsignedData = contractnotsignedyesterdayData;
const contractsignedData = contractsignedyesterdayData;
//console.log("reopendealsData",reopendealsData,"contractnotsignedData",contractnotsignedData,"contractsignedData",contractsignedData)

const sumCountsByUsername2 = (dataArray) => {
  const result = {};
  dataArray.forEach(item => {
    const { user_name, count } = item;
    result[user_name] = (result[user_name] || 0) + parseInt(count);
  });
  return result;
};



const reopendealsSummedData = sumCountsByUsername2(reopendealsData);
const contractnotsignedSummedData = sumCountsByUsername2(contractnotsignedData);
const contractsignedSummedData = sumCountsByUsername2(contractsignedData);




var dealctx = document.getElementById("DealChart").getContext("2d");
var myChartdeal = new Chart(dealctx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "Contract Signed",
        backgroundColor: '#4d0202',
        hoverBackgroundColor: '#4d0202',
        borderColor: '#4d0202',
        data: dataFromServer.usernames.map(username => contractsignedSummedData[username] || 0),
        barPercentage: 0.3,
      },
      {
        label: "Contract not Signed",
        backgroundColor: '#19355f', // Red color with transparency
        hoverBackgroundColor: '#19355f',
        borderColor: '#19355f',
        data: dataFromServer.usernames.map(username => contractnotsignedSummedData[username] || 0),
        barPercentage: 0.3,
      },
      {
        label: "Reopendeals",
        backgroundColor: '#9ea60d', // Green color with transparency
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
        data: dataFromServer.usernames.map(username => reopendealsSummedData[username] || 0),

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

// Filter data by custom date range
function filterDataByCustomRangedeal(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}

// Filter data by username
function filterDataByUsernamedeal(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}

function updateChartdeal(reopendealsData, contractsignedData, contractnotsignedData) {
  console.log("heelo",reopendealsData,contractsignedData,contractnotsignedData)
  const usernames = dataFromServer.usernames;
  const datasetCount = usernames.length;

  const contractsignedCounts = new Array(datasetCount).fill(0);
  const contractnotsignedCounts = new Array(datasetCount).fill(0);
  const reopendealsCounts = new Array(datasetCount).fill(0);

  // Check if the input data is an array
  if (Array.isArray(reopendealsData)) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      for (const item of contractsignedData) {
        if (item.user_name === username) {
          contractsignedCounts[i] += parseInt(item.count);
        }
      }

      for (const item of contractnotsignedData) {
        if (item.user_name === username) {
          contractnotsignedCounts[i] += parseInt(item.count);
        }
      }

      for (const item of reopendealsData) {
        if (item.user_name === username) {
          reopendealsCounts[i] += parseInt(item.count);
        }
      }
    }
  } else if (typeof reopendealsData === 'object' && reopendealsData !== null) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      contractsignedCounts[i] = parseInt(contractsignedData[username]) || 0;
      contractnotsignedCounts[i] = parseInt(contractnotsignedData[username]) || 0;
      reopendealsCounts[i] = parseInt(reopendealsData[username]) || 0;
    }
  }

  myChartdeal.data.datasets[0].data = contractsignedCounts;
  myChartdeal.data.datasets[1].data = contractnotsignedCounts;
  myChartdeal.data.datasets[2].data = reopendealsCounts;
  myChartdeal.update();
}


function handleDateFilterdeal() {
    const selectedValue = dateFilterdealDropdown.value;
    customDateFormfordeal.style.display = 'none';

    if (selectedValue === "yesterday2") {
        updateChartdeal(reopendealsyesterdayData, contractsignedyesterdayData, contractnotsignedyesterdayData);
    } else if (selectedValue === "last3days2") {
        updateChartdeal(reopendealsLast3DaysData, contractsignedLast3DaysData, contractnotsignedLast3DaysData);
    } else if (selectedValue === "custom2") {
        if (customDateFormfordeal.style.display === 'block') {
            customDateFormfordeal.style.display = 'none';
        } else {
            customDateFormfordeal.style.display = 'block';
        }
    }
}

// Function to handle click on the "custom2" option
dateFilterdealDropdown.addEventListener("click", function () {
    const selectedOption = dateFilterdealDropdown.options[dateFilterdealDropdown.selectedIndex];
    if (selectedOption.value === "custom2") {
        if (customDateFormfordeal.style.display === 'block') {
            customDateFormfordeal.style.display = 'none';
        } else {
            customDateFormfordeal.style.display = 'block';
        }
    }
});

function handleCustomDateFilterdeal(event) {
 customDateFormfordeal.style.display = 'none';
  event.preventDefault();
  const startDate = document.getElementById("startDate2").value;
  const endDate = document.getElementById("endDate2").value;
  const customReopendealsData = filterDataByCustomRangedeal(dataFromServer.reopendeals, startDate, endDate);
  const customContractsignedData = filterDataByCustomRangedeal(dataFromServer.contractsigned, startDate, endDate);
  const customContractnotsignedData = filterDataByCustomRangedeal(dataFromServer.contractnotsigned, startDate, endDate);
  updateChartdeal(customReopendealsData, customContractsignedData, customContractnotsignedData);
}


function handleUsernameFilterdeal(event) {
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterdealDropdown.value;
  if (selectedUsername === "Nofilter") {
    if (selectedDateFilter === "yesterday2") {
        updateChartdeal( reopendealsyesterdayData,contractsignedyesterdayData, contractnotsignedyesterdayData);
    } else if (selectedDateFilter === "last3days2") {
      updateChartdeal(reopendealsLast3DaysData,contractsignedLast3DaysData, contractnotsignedLast3DaysData);
    } else if (selectedDateFilter === "custom2") {
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;
      const customReopendealsData = filterDataByCustomRangedeal(dataFromServer.reopendeals, startDate, endDate);
       const customContractsignedData = filterDataByCustomRangedeal(dataFromServer.contractsigned, startDate, endDate);
       const customContractnotsignedData = filterDataByCustomRangedeal(dataFromServer.contractnotsigned, startDate, endDate);
      updateChartdeal(customReopendealsData,customContractsignedData , customContractnotsignedData);
    } else {
        updateChartdeal(reopendealsSummedData, contractsignedSummedData, contractnotsignedSummedData);
    }
  } else {
    if (selectedDateFilter === "yesterday2")  {
      var userDataYesterday = contractsignedyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsignedYesterday = contractnotsignedyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataRReopendealsYesterday = reopendealsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsYesterday,userDataYesterday, userDataContractnotsignedYesterday);
    } else if (selectedDateFilter === "last3days2") {
      var userDataLast3Days = contractsignedLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsignedLast3Days = contractnotsignedLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataRReopendealsLast3Days = reopendealsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsLast3Days, userDataLast3Days, userDataContractnotsignedLast3Days);

    } else if (selectedDateFilter === "custom2") {
    debugger
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;
      var customUserData =dataFromServer.contractsigned .filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataContractnotsigned = dataFromServer.contractnotsigned.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataReopendeals = dataFromServer.reopendeals.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartdeal(customUserDataReopendeals,customUserData, customUserDataContractnotsigned);


    } else {
      var userDataReopendeals = reopendealsSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userData = contractsignedSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsigned = contractnotsignedSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
       updateChartdeal(userDataReopendeals, userData, userDataContractnotsigned);

    }
  }
}


//candidateChart
function filterDataByCurrentWeekofcan(dataArray, key) {
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay()); // Get the first day of the current week
  const startOfWeekFormatted = startOfWeek.toISOString().slice(0, 10);

  return dataArray.filter(item => {
    const itemDate = new Date(item.date.replace(/[\s,]+/g, '-'));
    return itemDate >= startOfWeek;
  });
}

const interviewsyesterdayData = filterDataByCurrentWeekofcan(dataFromServer.interviews, 'interviews');
const resumesentsyesterdayData = filterDataByCurrentWeekofcan(dataFromServer.resumesents, 'resumesents');
const helpingsyesterdayData = filterDataByCurrentWeekofcan(dataFromServer.helpings, 'helpings');

function filterLastWeekofcan(dataArray, key) {
  const today = new Date();
  const endOfWeek = new Date(today);
  endOfWeek.setDate(today.getDate() - today.getDay() - 1); // Get the last day of the previous week
  const startOfWeek = new Date(endOfWeek);
  startOfWeek.setDate(endOfWeek.getDate() - 6); // Get the first day of the previous week

  const filteredData = [];

  for (let i = startOfWeek; i <= endOfWeek; i.setDate(i.getDate() + 1)) {
    const dayFormatted = i.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}

const interviewsLast3DaysData = filterLastWeekofcan(dataFromServer.interviews, 'interviews');
const resumesentsLast3DaysData = filterLastWeekofcan(dataFromServer.resumesents, 'resumesents');
const helpingsLast3DaysData = filterLastWeekofcan(dataFromServer.helpings, 'helpings');

const dateFilterDropdown = document.getElementById("dateFilterforcan");
dateFilterDropdown.addEventListener("change", handleDateFilter);
const customDateFormforcan = document.getElementById("customDateFormforcan");
customDateFormforcan.addEventListener("submit", handleCustomDateFilter);
const usernameFilterDropdown = document.getElementById("selectUsernamefor");
usernameFilterDropdown.addEventListener("change", handleUsernameFilter);

const interviewData = dataFromServer.interviews;
const resumesentData = dataFromServer.resumesents;
const helpingData = dataFromServer.helpings;


const sumCounts = (dataArray) => {
  const result = {};
  dataArray.forEach(item => {
    const { user_name, count } = item;
    result[user_name] = (result[user_name] || 0) + parseInt(count);
  });
  print(result)
  return result;
};



const interviewsSummedData = sumCounts(interviewsyesterdayData);
const resumesentsSummedData = sumCounts(resumesentsyesterdayData);
const helpingsSummedData = sumCounts(helpingsyesterdayData);
console.log(interviewsSummedData,resumesentsSummedData,helpingsSummedData)


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
        backgroundColor: '#19355f',
        hoverBackgroundColor: '#19355f',
        borderColor: '#19355f',
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
  console.log("candi", helpingData, resumesentData, interviewsData);
  const usernames = dataFromServer.usernames;
  const datasetCount = usernames.length;

  const helpingCounts = new Array(datasetCount).fill(0);
  const resumesentCounts = new Array(datasetCount).fill(0);
  const interviewsCounts = new Array(datasetCount).fill(0);

  // Check if the input data is an array
  if (Array.isArray(helpingData)) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      for (const item of helpingData) {
        if (item.user_name === username) {
          helpingCounts[i] += parseInt(item.count);
        }
      }

      for (const item of resumesentData) {
        if (item.user_name === username) {
          resumesentCounts[i] += parseInt(item.count);
        }
      }

      for (const item of interviewsData) {
        if (item.user_name === username) {
          interviewsCounts[i] += parseInt(item.count);
        }
      }
    }
  } else if (typeof helpingData === 'object' && helpingData !== null) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      resumesentCounts[i] = parseInt(resumesentData[username]) || 0;
      interviewsCounts[i] = parseInt(interviewsData[username]) || 0;
      helpingCounts[i] = parseInt(helpingData[username]) || 0;
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

    if (selectedValue === "yesterday1") {
        updateChartcandi(helpingsyesterdayData, resumesentsyesterdayData, interviewsyesterdayData);
    } else if (selectedValue === "last3days1") {
        updateChartcandi(helpingsLast3DaysData, resumesentsLast3DaysData, interviewsLast3DaysData);
    } else if (selectedValue === "custom1") {
        if (customDateFormforcan.style.display === 'block') {
            customDateFormforcan.style.display = 'none';
        } else {
            customDateFormforcan.style.display = 'block';
        }
    } else {
        updateChartcandi(helpingsSummedData, resumesentsSummedData, interviewsSummedData);
    }
}

// Function to handle click on the "custom1" option
dateFilterDropdown.addEventListener("click", function () {
    const selectedOption = dateFilterDropdown.options[dateFilterDropdown.selectedIndex];
    if (selectedOption.value === "custom1") {
        if (customDateFormforcan.style.display === 'block') {
            customDateFormforcan.style.display = 'none';
        } else {
            customDateFormforcan.style.display = 'block';
        }
    }
});

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

  if (selectedUsername === "Nofilter1") {
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
console.log(dataFromServer.candidateplacement,"dataFromServer.candidateplacement")
const xValues = dataFromServer.usernames;
const yValues = dataFromServer.usernames.map(username => {
  const userCount = dataFromServer.candidateplacement
    .filter(item => item.user_name === username)
    .reduce((sum, item) => sum + parseInt(item.count, 10), 0);
  return userCount;
});

const dynamicColors = Array.from({ length: xValues.length }, (_, index) => {
  const hue = (index * 37) % 360;
  return `hsl(${hue}, 70%, 50%)`;
});

const ctx = document.getElementById("placementChart").getContext("2d");

const chart = new Chart(ctx, {
  type: "pie",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: dynamicColors,
      data: yValues
    }]
  },
  options: {
    title: {
      display: true,
      text: "Candidates Placements"
    },
    maintainAspectRatio: false,
    responsive: true,
    width: 800,
    height: 700
  }
});

var startDateInput = document.getElementById("startDate");
var endDateInput = document.getElementById("endDate");


var dateFilterSelect = document.getElementById("dateFilter");
// Function to handle the change event on the date filter dropdown
dateFilterSelect.addEventListener("change", function () {
    var selectedValue = dateFilterSelect.value;
    console.log("selectedValue", selectedValue);

    if (selectedValue === "placecustom") {
        customDateForm.style.display = 'block'; // Display custom date form when "Custom" is selected
    } else {
        customDateForm.style.display = "none"; // Hide custom date form for other options
    }

    // Update the chart based on the selected filter
    if (selectedValue === "yesterday") {
        updateChart(filteredDatayesterday);
    } else if (selectedValue === "last3days") {
        updateChart(filteredlast3days);
    } else if (selectedValue === "all") {
        updateChartWithDefaultData();
    }
});

// Function to handle click on the "placecustom" option
dateFilterSelect.addEventListener("click", function () {
    var selectedOption = dateFilterSelect.options[dateFilterSelect.selectedIndex];
    if (selectedOption.value === "placecustom") {
    console.log("Custom option clicked again");
        customDateForm.style.display = 'block'; // Display custom date form when "Custom" is selected
    } else {
        customDateForm.style.display = "none"; // Hide custom date form for other options
    }
});

var customData;

var customDateForm = document.getElementById("customDateForm");
customDateForm.style.display = "none";
//function filterDataForToday() {
//  const today = new Date().toLocaleDateString();
//  return dataFromServer.candidateplacement.filter(item => item.date === today);
//}

function filterDataForYesterday() {
    const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay()); // Get the first day of the current week

  const endOfWeek = new Date(today);
  endOfWeek.setDate(startOfWeek.getDate() + 6); // Get the last day of the current week

  return dataFromServer.candidateplacement.filter(item => {
    const itemDate = new Date(item.date);
    return itemDate >= startOfWeek && itemDate <= endOfWeek;
  });

}

function filterDataForLast3Days() {
  const today = new Date();
  const endOfLastWeek = new Date(today);
  endOfLastWeek.setDate(today.getDate() - today.getDay() - 1); // Get the last day of the previous week

  const startOfLastWeek = new Date(endOfLastWeek);
  startOfLastWeek.setDate(endOfLastWeek.getDate() - 6); // Get the first day of the previous week

  return dataFromServer.candidateplacement.filter(item => {
    const itemDate = new Date(item.date);
    return itemDate >= startOfLastWeek && itemDate <= endOfLastWeek;
  });
}

//var todayData = filterDataForToday();
var filteredDatayesterday = filterDataForYesterday();
var filteredlast3days = filterDataForLast3Days();

customDateForm.addEventListener("submit", function (event) {
  event.preventDefault();
  customDateForm.style.display = "none";

  var startDate = startDateInput.value;
  var endDate = endDateInput.value;
  customData = dataFromServer.candidateplacement.filter(function (item) {
    var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });

  // Update the chart with the custom data
  updateChartWithCustomData(startDate, endDate);
});

function updateChart(dataset) {
  yValues.length = 0; // Clear the existing array
  xValues.forEach(username => {
    const userCount = dataset
      .filter(item => item.user_name === username)
      .reduce((sum, item) => sum + parseInt(item.count, 10), 0);
    yValues.push(userCount);
  });
  chart.data.datasets[0].data = yValues;
  chart.update();
}

function updateChartWithCustomData(startDate, endDate) {
  yValues.length = 0; // Clear the existing array

  // Update yValues based on custom data
  xValues.forEach(username => {
    const userCount = customData
      .filter(item => item.user_name === username)
      .reduce((sum, item) => sum + parseInt(item.count, 10), 0);
    yValues.push(userCount);
  });

  // Update the chart
  chart.data.datasets[0].data = yValues;
  chart.update();
}
function updateChartWithDefaultData() {
  yValues.length = 0; // Clear the existing array
  xValues.forEach(username => {
    const userCount = dataFromServer.candidateplacement
      .filter(item => item.user_name === username)
      .reduce((sum, item) => sum + parseInt(item.count, 10), 0);
    yValues.push(userCount);
  });

  // Update the chart
  chart.data.datasets[0].data = yValues;
  chart.update();
}
updateChart(filteredDatayesterday);

}
}
