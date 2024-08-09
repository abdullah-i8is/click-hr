function showDiv(divId) {
    var div = document.getElementById(divId);
    var allDivs = document.getElementsByClassName('recuriting-did')[0].children;

    for (var i = 0; i < allDivs.length; i++) {
        if (allDivs[i].id === divId) {
            allDivs[i].style.display = 'block';
        } else {
            allDivs[i].style.display = 'none';
        }
    }
}
function showDivform(divId) {
    var div1 = document.getElementById(divId);
    var div2 = document.getElementById('Incidentdiv');
    var div3 = document.getElementById('Requestforleavediv');

   
    if (div1 === div2) {
        div2.style.display = 'block';
        div3.style.display = 'none';
    }else if (div1 === div3) {
        div3.style.display = 'block';
        div2.style.display = 'none';
    } else {
        div2.style.display = 'none';
    }
}

function showmaincontent(divId) {
    var div = document.getElementById(divId);
    var allDivs = document.getElementsByClassName('contentchanging')[0].children;

    for (var i = 0; i < allDivs.length; i++) {
        if (allDivs[i].id === divId) {
            allDivs[i].style.display = 'block';
        } else {
            allDivs[i].style.display = 'none';
        }
    }
}