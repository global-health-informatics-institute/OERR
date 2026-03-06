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

  // Move shared keyboard to the active tab (if an anchor exists there).
  const tab = event.target.closest(".tab");
  const anchor = tab ? tab.querySelector(".keyboard-anchor") : null;
  const keyboardContainer = document.querySelector(".simple-keyboard");
  if (anchor && keyboardContainer && keyboardContainer.parentElement !== anchor) {
    anchor.appendChild(keyboardContainer);
  }

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
  activeInput.value = input;
  activeInput.dispatchEvent(new Event("input", { bubbles: true }));

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
