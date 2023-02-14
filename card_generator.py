import openai
import requests
import os


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()


openai.api_key = read_file("apikey.txt")
prompt = read_file("prompt.txt")


def generate_flashcards(information):
    text = prompt + "\n" + information + "\n\n Output:\n"
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text,
        max_tokens=4096 - int(len(text) / 3),  # this should be fixed
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


def add_card_basic(question, answer, deck_name="AI IM Deck"):
    action = "addNote"
    params = {
        "note": {
            "deckName": deck_name,
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


def make_cards_from_chunk(filename):
    directory = "generated_cards"
    text = ""
    with open(f"chunks/{filename}.txt") as f:
        text = f.read()
    if not text:
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}_CARDS.txt", "w") as f:
        cards = generate_flashcards(text)
        f.write("\n".join([f"Q:{q}\nA:{a}\n" for q, a in cards]))


# flashcards = generate_flashcards(prompt + "\n" + information + "\n\n Output:\n")
# for q, a in flashcards:
#     make_card_basic(q, a)

make_cards_from_chunk("Asthma")
