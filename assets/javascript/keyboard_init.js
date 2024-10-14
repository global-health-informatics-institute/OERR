let Keyboard = window.SimpleKeyboard.default;

let selectedInput;
let inputElement = document.querySelector("#input20");
let charLength = inputElement ? inputElement.maxLength : null;

let keyboard = new Keyboard({
  onChange: input => onChange(input),
  onKeyPress: button => onKeyPress(button),
  layout: {
    'default': [
      '1 2 3 4 5 6 7 8 9 0 {bksp}',
      'q w e r t y u i o p',
      '{lock} a s d f g h j k l',
      'z x c v b n m , . {space}'
    ],
    'shift': [
      '1 2 3 4 5 6 7 8 9 0 {bksp}',
      'Q W E R T Y U I O P',
      '{lock} A S D F G H J K L',
      'Z X C V B N M , . {space}'
    ],
    display: {
      '{bksp}': 'bksp',
      '{space}': 'space',
      '{lock}': 'CAPS'
    }
  }
});

document.querySelectorAll(".input").forEach(input => {
  input.addEventListener("focus", onInputFocus);
  input.addEventListener("input", onInputChange);
});

function onInputFocus(event) {
  selectedInput = `#${event.target.id}`;
  console.log("onInputFocus");
  keyboard.setOptions({
    inputName: event.target.id
  });
}

function onInputChange(event) {
  console.log("onInputChange");
  keyboard.setInput(event.target.value, event.target.id);
}

function onChange(input) {
  console.log("onChange");

  if (inputElement && charLength && charLength > 0) {
    
    // Limit the input to charLength
    if (input.length > charLength && !isBackSpace(lastPressedButton)) {
      input = input.substring(0, charLength);
    }

    // Allow input if it's within the maxLength or backspace is pressed
    if (inputElement.value.length < charLength || isBackSpace(lastPressedButton)) {
      document.querySelector(selectedInput || ".input").value = input;
    }
  } else {
    // If no maxlength or char length is fine, update the input
    document.querySelector(selectedInput || ".input").value = input;
  }

  // Update keyboard's internal state with the (possibly truncated) input
  keyboard.setInput(input);
}


function isBackSpace(button) {
  return (button === "{bksp}") ? 1 : 0;
}

let lastPressedButton = ""; // Variable to track the last pressed key

function onKeyPress(button) {
  console.log("onKeyPress");
  
  // Store the pressed key
  lastPressedButton = button;

  /**
   * Shift functionality
   */
  if (button === "{lock}" || button === "{shift}") handleShiftButton();
}

function handleShiftButton() {
  let currentLayout = keyboard.options.layoutName;
  let shiftToggle = currentLayout === "default" ? "shift" : "default";
  console.log("handleShiftButton");
  keyboard.setOptions({
    layoutName: shiftToggle
  });
}
