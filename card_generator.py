import openai
import requests


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()


openai.api_key = read_file("apikey.txt")
prompt = read_file("prompt.txt")
information = read_file("notes.txt")


def generate_flashcards(text):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text,
        max_tokens=4096 - len(text),
        n=1,
        stop=None,
        temperature=.1,
    )
    lines = completions.choices[0].text.strip().split("\n")
    result = []
    question = None
    for line in lines:
        if line.startswith("Q:"):
            question = line[2:].strip()
        elif line.startswith("A:"):
            result.append((question, line[2:].strip()))

    return result


def make_card_basic(question, answer):
    action = "addNote"
    params = {
        "note": {
            "deckName": "AI IM Deck",
            "modelName": "Basic",
            "fields": {
                "Front": question,
                "Back": answer
            },
            "options": {
                "allowDuplicate": False
            },
            "tags": []
        }
    }
    response = requests.post(
        "http://localhost:8765",
        json={
            "action": action,
            "params": params,
            "version": 6
        }
    )
    if response.status_code != 200:
        raise Exception("Failed to add flashcard: " + response.text)


flashcards = generate_flashcards(prompt + "\n" + information + "\n\n Output:\n")
for q, a in flashcards:
    make_card_basic(q, a)
