import openai
import requests
import os
from doc_parser import create_chunks


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()


openai.api_key = read_file("apikey.txt")
prompt = read_file("prompt.txt")


def generate_flashcards(information):
    text = prompt + "\n" + information + "\n\n Output:\n"
    try:
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            max_tokens=4096 - int(len(text) / 3),  # this should be fixed
            n=1,
            stop=None,
            temperature=.1,
        )
    except openai.error.InvalidRequestError as err:
        print(err)
        m = err.error.message
        try:
            prompt_tokens = int(m[m.index("(") + 1:].split(' ')[0])
        except Exception as e:
            print(str(e))
            raise err

        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            max_tokens=4096 - prompt_tokens,  # this should be fixed
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
    with open(f"chunks/{filename}.txt") as f:
        text = f.read()
    if not text:
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}_CARDS.txt", "w") as f:
        cards = generate_flashcards(text)
        f.write("\n".join([f"Q:{q}\nA:{a}\n" for q, a in cards]))


def process_all_chunks(skip_existing=True):
    files = os.listdir("chunks")
    existing = [x[:-10] for x in os.listdir("generated_cards")]
    for file in files:
        if skip_existing and file[:-4] in existing:
            print("SKIPPING " + file)
            continue
        print("starting on cards for " + file)
        make_cards_from_chunk(file[:-4])
        print("created card file for " + file + "\n")


def make_cards_from_files():
    files = os.listdir("generated_cards")
    qs = []
    for file in files:
        with open(f"generated_cards/{file}", "r") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 3):
                try:
                    qs.append((lines[i][2:], lines[i + 1][2:]))
                except Exception as e:
                    print(e)
    for q, a in qs:
        add_card_basic(q, a)


def __main__():
    create_chunks()
    process_all_chunks()
    make_cards_from_files()