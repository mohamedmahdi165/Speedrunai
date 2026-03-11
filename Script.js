const iframe = document.getElementById('iframe');
const urlInput = document.getElementById('url');
const historyStack = [];
let historyIndex = -1;

function navigate() {
  let input = urlInput.value.trim();
  let url;

  // Check if input looks like a URL
  if (input.includes('.') && !input.includes(' ')) {
    url = input.startsWith('http') ? input : 'https://' + input;
  } else {
    // Treat as search query
    url = 'https://www.google.com/search?q=' + encodeURIComponent(input);
  }

  iframe.src = url;

  // Update history
  historyStack.splice(historyIndex + 1);
  historyStack.push(url);
  historyIndex++;
}

function goBack() {
  if (historyIndex > 0) {
    historyIndex--;
    iframe.src = historyStack[historyIndex];
    urlInput.value = historyStack[historyIndex];
  }
}

function goForward() {
  if (historyIndex < historyStack.length - 1) {
    historyIndex++;
    iframe.src = historyStack[historyIndex];
    urlInput.value = historyStack[historyIndex];
  }
}

function reloadPage() {
  iframe.src = iframe.src;
}
