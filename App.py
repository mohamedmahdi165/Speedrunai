# Install libraries
!pip -q install transformers torch wikipedia sympy googlesearch-python gradio

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import wikipedia
from sympy import sympify
from googlesearch import search
import re
import gradio as gr

BOT_NAME = "SpeedRun"

print("Loading model...")

model_name = "huggingfacetb/SmolLM2-135M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

print("SpeedRun ready!")

# ---------------- GREETINGS ----------------

def handle_greetings(text):
    greetings = ["hello","hi","hey","good morning","good evening"]
    if text.lower().strip() in greetings:
        return "Hello! How can I help you?"
    return None


# ---------------- NUMBER WORDS ----------------

number_words = {
"zero":"0","one":"1","two":"2","three":"3","four":"4",
"five":"5","six":"6","seven":"7","eight":"8","nine":"9",
"ten":"10","eleven":"11","twelve":"12"
}

def words_to_numbers(text):

    words = text.lower().split()

    converted = []

    for w in words:
        if w in number_words:
            converted.append(number_words[w])
        else:
            converted.append(w)

    return " ".join(converted)


# ---------------- MATH SYSTEM ----------------

def normalize_math(text):

    text = words_to_numbers(text)

    text = text.lower()

    text = text.replace("times","*")
    text = text.replace("multiplied by","*")
    text = text.replace("x","*")

    text = text.replace("plus","+")
    text = text.replace("minus","-")

    text = text.replace("divided by","/")
    text = text.replace("over","/")

    return text


def extract_math(text):

    text = normalize_math(text)

    match = re.findall(r"[0-9\.\+\-\*/\(\)]+", text)

    if match:
        return "".join(match)

    return None


def solve_math(text):

    try:

        expr = extract_math(text)

        if not expr:
            return None

        expr = expr.replace("^","**")

        result = sympify(expr).evalf()

        if result == int(result):
            result = int(result)

        return f"The answer is {result}"

    except:
        return None


# ---------------- WIKIPEDIA ----------------

def search_wiki(q):
    try:
        return wikipedia.summary(q, sentences=2)
    except:
        try:
            results = wikipedia.search(q)
            if results:
                return wikipedia.summary(results[0], sentences=2)
        except:
            pass
    return None


# ---------------- GOOGLE FALLBACK ----------------

def google_fallback(q):
    try:
        results = list(search(q, num_results=2))
        if results:
            return "Try these links: " + ", ".join(results)
    except:
        pass
    return "Sorry, I couldn't find an answer."


# ---------------- AI RESPONSE ----------------

def ask_ai(prompt):

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=40,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    reply = text.replace(prompt, "").strip()

    return reply


# ---------------- CHAT LOGIC ----------------

def chat(user_input, history):

    history = history or []
    response = None
    text = user_input.lower()

    # greetings
    response = handle_greetings(user_input)

    # math
    if not response:
        math_answer = solve_math(user_input)
        if math_answer:
            response = math_answer

    # factual questions
    factual_keywords = [
        "who","who is","who's",
        "what","what is","what's",
        "when","where",
        "define","explain"
    ]

    if not response and any(k in text for k in factual_keywords):
        response = search_wiki(user_input)

    # short queries
    if not response and len(user_input.split()) <= 3:
        response = search_wiki(user_input)

    # AI fallback
    if not response:
        response = ask_ai(user_input)

    # final fallback
    if not response or response.strip()=="":
        response = google_fallback(user_input)

    response = f"{BOT_NAME}: {response}"

    history.append((user_input, response))

    return history, history


# ---------------- UI ----------------

with gr.Blocks() as demo:

    gr.Markdown("## SpeedRun AI")

    chatbot = gr.Chatbot()

    msg = gr.Textbox(placeholder="Ask something...")

    clear = gr.Button("Clear Chat")

    msg.submit(chat,[msg,chatbot],[chatbot,chatbot])

    clear.click(lambda:[],None,chatbot)

demo.launch(share=True)
