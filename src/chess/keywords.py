import pprint



def get_labels():
    mapping = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
    }
    labels = [
        'pawn',
        'king',
        'queen',
        'rook',
        'bishop',
        'knight',
        'move',
        'direction',
        'black',
        'white',
        'castle',
        'en passant',
        'promotion',
        'check',
        'checkmate',
        'stalemate',
        'counter',
        'defense',
        'response',
        'control',
    ]
    #for letter in range(8):
    #    for number in range(8):
    #        coordinate = ""
    #        
    #        labels.append(coordinate)


    return labels

def apply_labels(labels):
    new_documents = []

    with open("data\info.txt", 'r', encoding='utf-8') as file:
        document = file.readlines()
    documents = [move.strip().lower() for move in document if move.strip()]
    
    for document in documents:
        applied_labels = []
        for label in labels:
            if label in document:
                applied_labels.append(label)
        
        row = [applied_labels, document]
        new_documents.append(row)

    return new_documents

new_documents = apply_labels(get_labels())
#new_documents = [document for document in new_documents if len(document[0]) == 0]
pprint.pprint(new_documents)