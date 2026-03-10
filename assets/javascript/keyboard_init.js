let Keyboard = window.SimpleKeyboard.default;

let selectedInput;

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
  const activeInput = document.querySelector(selectedInput || ".input");
  if (!activeInput) return;

  if (activeInput.readOnly || activeInput.disabled) {
    keyboard.setInput(activeInput.value || "", activeInput.id);
    return;
  }

  let newValue = input;
  const maxLength = activeInput.maxLength;
  if (typeof maxLength === "number" && maxLength > 0 && newValue.length > maxLength) {
    newValue = newValue.substring(0, maxLength);
  }

  activeInput.value = newValue;
  activeInput.dispatchEvent(new Event("input", { bubbles: true }));
  keyboard.setInput(newValue, activeInput.id);
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
