function sick_restriction() {
    var inputField = document.getElementById("restricted");
    var controll = document.getElementById("controll");
    var max_char = controll.value

    console.log(max_char);
    // Function to enforce the max length restriction
    function enforceMaxLength() {
        var inputValue = inputField.value;
        
        // Log the current input value before trimming
        console.log("Current input value before trim: " + inputValue);
        
        // If the input length exceeds max_char, trim the extra characters
        if (inputValue.length > max_char) {
            inputField.value = inputValue.substring(0, max_char);
        }
    }

    // Set the maxlength attribute (for additional native restriction)
    inputField.maxLength = max_char;

    // Listen to multiple events to catch all changes to the input field
    inputField.addEventListener('input', enforceMaxLength);
    inputField.addEventListener('change', enforceMaxLength);
    inputField.addEventListener('keyup', enforceMaxLength);
    inputField.addEventListener('keydown', enforceMaxLength);
    inputField.addEventListener('paste', function() {
        // Use a timeout to allow the paste operation to complete before trimming
        setTimeout(enforceMaxLength, 0);
    });

    // MutationObserver to detect external changes to the input field's value
    var observer = new MutationObserver(function() {
        enforceMaxLength();
        console.log("changes occured");// Enforce max length after every DOM mutation
    });

    // Start observing the input field for any changes
    observer.observe(inputField, { characterData: true, childList: true, subtree: true });

    // Alternatively, listen for DOM modifications (a broader event)
    console.log("This run")
}
