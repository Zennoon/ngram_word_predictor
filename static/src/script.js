const mainInput = document.getElementById("main-input");
const hintInput = document.getElementById("hint-input");

const nInput = document.getElementById("n-input");
const nValue = document.getElementById("n-value");

const kInput = document.getElementById("k-input");
const kValue = document.getElementById("k-value");

const suggestionsContainer = document.getElementById("suggestions-container");
const errorText = document.getElementById("error-text");
const wordsCount = document.getElementById("words-count");

mainInput.addEventListener("input", async (e) => {
  const n = Number(nValue.innerText);
  suggestionsContainer.innerHTML = "<div class='flex items-center gap-4'>";
  for (let i = 0; i < 10; i++) {
    suggestionsContainer.innerHTML +=
      "<div class='w-16 h-6 bg-gray-800 border border-gray-700 rounded-xl animate-pulse'></div>";
  }
  suggestionsContainer.innerHTML += "</div>";
  const text = e.target.value.toLowerCase();
  suggestionsContainer.innerHTML = "<div class='flex items-center gap-4'>";
  for (let i = 0; i < 10; i++) {
    suggestionsContainer.innerHTML +=
      "<div class='w-10 h-4 bg-gray-900 border border-gray-700 rounded-xl animate-pulse'></div>";
  }
  suggestionsContainer.innerHTML += "</div>";
  console.log("text", text);

  if (text == "") {
    wordsCount.innerText = 0;
    return;
  }
  const words = text.trim().split(" ");
  console.log("words", words);

  wordsCount.innerText = words.length;

  let history;
  let prefix;

  if (text.at(-1) == " ") {
    history = words.slice(-n).join(" ");
    prefix = "";
  } else {
    history = words.slice(-n, -1).join(" ");
    prefix = words.at(-1);
  }

  const response = await fetch("/most_prob_words", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      n: Number(nValue.innerText),
      history,
      prefix,
      k: Number(kValue.innerText),
    }),
  });


  if (!response.ok) {
    errorText.innerText =
      "An unexpected error occurred. Please try typing again.";
    hintInput.innerText = "";
    return;
  }

  const result = await response.json();
  console.log(result);
  if (result.status === "success") {
    suggestionsContainer.innerHTML = "";
    for (let wordTuple of result.data.words) {
      suggestionsContainer.innerHTML += `
            <button class="flex items-center gap-2 text-sm px-3 py-1 bg-gray-800 border border-gray-600 rounded-2xl">
                <span class="amharic-text">${wordTuple[0]}</span>
                <span class="text-emerald-400">${wordTuple[1].toFixed(2)}</span>
              </button>
        `;
    }

    if (result.data.words.length > 0) {
      const topSuggestion = result.data.words[0][0];
      console.log("Top Suggestion", topSuggestion);
      if (prefix) {
        console.log("Prefix", prefix);
        if (words.length > 1) {
          hintInput.value = words.slice(0, -1).concat(topSuggestion).join(" ");
        } else {
          hintInput.value = topSuggestion;
        }
      } else {
        console.log("words", words);
        if (words.length && words[0].length) {
          hintInput.value = words.concat(topSuggestion).join(" ");
        } else {
          hintInput.value = topSuggestion;
        }
      }
    } else {
      hintInput.value = "";
      suggestionsContainer.innerHTML = "No suggestions";
    }
    return;
  }
});

mainInput.addEventListener("keydown", (e) => {
  if ((e.key == "Tab" || e.key == "Enter") && hintInput.value) {
    e.preventDefault();
    mainInput.value = hintInput.value;
    hintInput.value = "";
  }
});

nInput.addEventListener("input", (e) => {
  nValue.innerText = e.target.value;
});

kInput.addEventListener("input", (e) => {
  kValue.innerText = e.target.value;
});
