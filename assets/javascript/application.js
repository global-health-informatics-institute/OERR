var isCapsLock = false;

//function to add navigation buttons to footer
function addNavButtons(){
    if (navButtons == undefined ) return
    var footer = document.getElementById('navFooter')
    for(let i=0; i < navButtons.length; i++)
    {
        footer.innerHTML +=navButtons[i]
    }
}

function showMainTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("maintabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("maintablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

//Function to hide modal dialog
function hideDialog(url){
    window.location=url
}

//Function to focus on barcosde input field
function checkBarcode()
{
    var barcodeTxt = document.getElementById("barcode");
    if (barcodeTxt.value.trim().length > 1 && barcodeTxt.value.trim().length == barcode_length) {
        barcodeTxt.value = barcodeTxt.value.trim().replace(/\$/, "").replace(/\-/,"")
        if (barcodeTxt.value.toUpperCase().length >= 5)
        {
            document.barcodeScan.submit()
        }
        else
        {
            //barcodeTxt.value = "";
            initializeListener();
        }
    }
    else
    {
        initializeListener();
    }
    barcode_length = barcodeTxt.value.trim().length;
}

//Function to initialize listener for barcode scanning
function initializeListener()
{
    document.getElementById("barcode").focus();
    timerHand = setTimeout(function () {
        checkBarcode();
    }, 1500);
}

//Wizard form javascript
function showTab(n) {
    // This function will display the specified tab of the form...
    var x = document.getElementsByClassName("tab");
    x[n].style.display = "block";
    //... and fix the Previous/Next buttons:
    if (n == 0) {
        document.getElementById("prevBtn").style.display = "none";
    } else {
        document.getElementById("prevBtn").style.display = "inline";
    }
    if (n == (x.length - 1)) {
        document.getElementById("nextBtn").innerHTML = "Submit";
    } else {
        document.getElementById("nextBtn").innerHTML = "Next";
    }
    //... and run a function that will display the correct step indicator:
    fixStepIndicator(n)
}

function nextPrev(n) {
    // This function will figure out which tab to display
    var x = document.getElementsByClassName("tab");
    // Exit the function if any field in the current tab is invalid:
    if (n == 1 && !validateForm()) return false;
    // Hide the current tab:
    x[currentTab].style.display = "none";
    // Increase or decrease the current tab by 1:
    currentTab = currentTab + n;
    // if you have reached the end of the form...
    if (currentTab >= x.length) {
        // ... the form gets submitted:
        document.getElementById("regForm").submit();
        return false;
    }
    // Otherwise, display the correct tab:
    showTab(currentTab);
}

function validateForm() {
    // This function deals with validation of the form fields
    var x, y, i, valid = true;
    x = document.getElementsByClassName("tab");
    y = x[currentTab].getElementsByTagName("input");

    if (y[0].required){
        switch(y[0].type) {
            case 'text':
                if (y[0].value.trim() == "") {
                    y[0].className += " invalid";
                    // and set the current valid status to false
                    valid = false;
                }
                break;
            case 'radio':
                if (document.querySelector('input[name ='+y[0].name +']:checked') == null){
                    valid = false;
                }
                break;
            case 'checkbox':
                if (document.querySelector('input[name ="'+y[0].name +'"]:checked') == null){
                    valid = false;
                }

                break;
        }
    }


    // If the valid status is true, mark the step as finished and valid:
    if (valid) {
        document.getElementsByClassName("step")[currentTab].className += " finish";
    }
    return valid; // return the valid status
}

function filterDoctors() {
    // Get the search input value
    var input = document.getElementById('doctor-search');
    var filter = input.value.toLowerCase();
    
    // Get the doctor list
    var doctorList = document.getElementById('doctor-list');
    var doctors = doctorList.getElementsByTagName('li');

    // Loop through all list items, and hide those that don't match the search query
    for (var i = 0; i < doctors.length; i++) {
        var label = doctors[i].getElementsByTagName("label")[0];
        if (label) {
            var txtValue = label.textContent || label.innerText;
            if (txtValue.toLowerCase().indexOf(filter) > -1) {
                doctors[i].style.display = "";
            } else {
                doctors[i].style.display = "none";
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('doctor-search');
    var keyboard = document.getElementById('keyboard');

    input.addEventListener('focus', function () {
        keyboard.style.display = 'block';
    });

    document.addEventListener('click', function (event) {
        // Check if the click is outside of the input and keyboard
        if (!input.contains(event.target) && !keyboard.contains(event.target)) {
            keyboard.style.display = 'none';
        }
    });
});

function typeKey(key) {
    var input = document.getElementById('doctor-search');
    if (key === 'Backspace') {
        input.value = input.value.slice(0, -1); // Remove last character
    } else {
        input.value += isCapsLock && key.length === 1 ? key.toUpperCase() : key;
    }
    // Trigger the filter function after typing
    filterDoctors();
    input.focus(); // Maintain focus on the input after typing
}

function toggleCapsLock() {
    isCapsLock = !isCapsLock;
    updateKeyboardKeys();
    var capsButton = document.getElementById('caps');
    capsButton.classList.toggle('active'); // Toggle the active class on the Caps button
    document.getElementById('doctor-search').focus();
}


function updateKeyboardKeys() {
    var keys = document.querySelectorAll('#keyboard button');
    keys.forEach(function(key) {
        if (key.textContent.length === 1) { // Check if the button is a single character key
            key.textContent = isCapsLock ? key.textContent.toUpperCase() : key.textContent.toLowerCase();
        }
    });
}

function fixStepIndicator(n) {
    // This function removes the "active" class of all steps...
    var i, x = document.getElementsByClassName("step");
    for (i = 0; i < x.length; i++) {
        x[i].className = x[i].className.replace(" active", "");
    }
    //... and adds the "active" class on the current step:
    x[n].className += " active";
}

function idleTimer(){
    const idleDurationSecs = 900;    // X number of seconds
    const redirectUrl = '/logout';  // Redirect idle users to this URL
    let idleTimeout; // variable to hold the timeout, do not modify

    const resetIdleTimeout = function() {
        // Clears the existing timeout
        if(idleTimeout) clearTimeout(idleTimeout);

        // Set a new idle timeout to load the redirectUrl after idleDurationSecs
        idleTimeout = setTimeout(() => window.location = redirectUrl, idleDurationSecs * 1000);
    };

    // Init on page load
    resetIdleTimeout();

    // Reset the idle timeout on any of the events listed below
    ['click', 'touchstart', 'mousemove','mousedown'].forEach(evt =>
        document.addEventListener(evt, resetIdleTimeout, false)
    );
};

function powerMonitor(){
    console.log("Check charge state")
    let powerTimeout; // variable to hold the timeout, do not modify

    const resetPowerTimeout = function() {
        // Clears the existing timeout
        if(powerTimeout) clearTimeout(powerTimeout);
        // Set a new idle timeout to load the redirectUrl after idleDurationSecs
        powerTimeout = setTimeout(() => eval('checkChargeStatus'), 1000);
    };

}

function checkChargeStatus(){
    var xhr = new XMLHttpRequest();
    var url = "/get_charge_state";
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/text");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var results = JSON.parse(xhr.responseText)
            if(results)
            {
                console.log(results)
                var battery = document.getElementById("batteryState");

                if (results["current_power"] <= 0 && results["checkCharging"] == false)
                {
                    if (deviceOff == false){
                        window.location = "/low_voltage"
                    }
                }
                else if (results["checkCharging"] == true && deviceOff)
                {
                    window.location = "/"
                }
                else{
                    if(results["checkCharging"] == false){
                        battery.innerHTML ="&nbsp;";
                    }
                    else
                    {
                        document.getElementById("batteryState").innerHTML ="<span style='padding-left:45%;font-weight:bold;'>&#9889;</span>";
                    }
                    battery.class = results["power_class"]
                    battery.style.width = results["current_power"]
                }
            }
        }
    };
    xhr.send();


}
