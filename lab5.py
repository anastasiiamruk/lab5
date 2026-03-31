import sqlite3
import time

DB_NAME = "lab3.db"

chain = []
votes = set()
blocks = {}


class Block:
    def __init__(self, id, view):
        self.id = id
        self.view = view

    def __str__(self):
        return f"{self.id} (view={self.view})"


class Vote:
    def __init__(self, block_id):
        self.block_id = block_id

    def __eq__(self, other):
        return self.block_id == other.block_id

    def __hash__(self):
        return hash(self.block_id)


def try_add_to_chain():
    global chain

    for block_id in sorted(blocks, key=lambda x: blocks[x].view):
        block = blocks[block_id]

        if block not in chain and Vote(block.id) in votes:
            chain.append(block)


def process_events():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, type, ref_id FROM EVENT_STREAM
    WHERE processed = 0
    ORDER BY id
    """)

    events = cursor.fetchall()

    for event_id, e_type, ref_id in events:

        if e_type == "block":
            cursor.execute("SELECT id, view FROM BLOCKS WHERE id = ?", (ref_id,))
            row = cursor.fetchone()
            if row:
                block = Block(*row)
                blocks[block.id] = block

        elif e_type == "vote":
            votes.add(Vote(ref_id))

        cursor.execute(
            "UPDATE EVENT_STREAM SET processed = 1 WHERE id = ?",
            (event_id,)
        )

    conn.commit()
    conn.close()

    try_add_to_chain()


if __name__ == "__main__":
    while True:
        process_events()

        print("\nCurrent chain:")
        for b in chain:
            print(b)

        time.sleep(3)
