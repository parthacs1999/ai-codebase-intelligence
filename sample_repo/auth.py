USERS = {
    "alice": "secret123",
    "bob": "python456",
}


def login(username, password):
    return USERS.get(username) == password


def main():
    attempts = [
        ("alice", "secret123"),
        ("bob", "wrong-password"),
    ]

    for username, password in attempts:
        if login(username, password):
            print(f"{username} logged in")
        else:
            print(f"{username} was not authenticated")


if __name__ == "__main__":
    main()
